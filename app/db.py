import json
import psycopg2
from pgvector.psycopg2 import register_vector
from app.config import DB_CONFIG
from app.schemas import CandidateProfile


def get_connection():
	conn = psycopg2.connect(**DB_CONFIG)
	register_vector(conn)
	return conn


def _total_experience_years(profile: CandidateProfile) -> float:
	"""Sum of work_experience durations (assumes non-overlapping jobs)."""
	return round(sum(job.duration for job in profile.work_experience), 1)


def insert_candidate(profile: CandidateProfile, profile_summary: str, embedding: list[float]) -> int:
	"""Stores the FULL structured profile -- personal_info, work_experience[],
	educations[], skills[], certificates[], language[] -- not just a flattened
	name/email/phone/summary. Also fans skills out into candidate_skills so
	"X with N+ years of skill Y" can be a precise SQL filter later, not just
	a fuzzy embedding match.
	"""
	total_exp = _total_experience_years(profile)

	conn = get_connection()
	try:
		with conn:
			with conn.cursor() as cur:
				cur.execute(
					"""
					INSERT INTO candidates (
						name, email, phone_no, address, social,
						total_experience_years,
						work_experience, educations, skills, certificates, language,
						profile_summary, embedding
					) VALUES (
						%s, %s, %s, %s, %s,
						%s,
						%s, %s, %s, %s, %s,
						%s, %s
					)
					ON CONFLICT (email) WHERE email != ''
					DO UPDATE SET
						name = EXCLUDED.name,
						phone_no = EXCLUDED.phone_no,
						address = EXCLUDED.address,
						social = EXCLUDED.social,
						total_experience_years = EXCLUDED.total_experience_years,
						work_experience = EXCLUDED.work_experience,
						educations = EXCLUDED.educations,
						skills = EXCLUDED.skills,
						certificates = EXCLUDED.certificates,
						language = EXCLUDED.language,
						profile_summary = EXCLUDED.profile_summary,
						embedding = EXCLUDED.embedding
					RETURNING id;
					""",
					(
						profile.personal_info.name,
						profile.personal_info.email,
						profile.personal_info.phone_no,
						profile.personal_info.address,
						json.dumps(profile.personal_info.social),
						total_exp,
						json.dumps([w.model_dump() for w in profile.work_experience]),
						json.dumps([e.model_dump() for e in profile.educations]),
						json.dumps([s.model_dump() for s in profile.skills]),
						json.dumps(profile.certificates),
						json.dumps(profile.language),
						profile_summary,
						embedding,
					),
				)
				candidate_id = cur.fetchone()[0]

				# Refresh normalized skill rows (delete + reinsert is simplest
				# and correct for the upsert case above).
				cur.execute("DELETE FROM candidate_skills WHERE candidate_id = %s", (candidate_id,))
				for s in profile.skills:
					cur.execute(
						"""
						INSERT INTO candidate_skills (candidate_id, skill_name, experience)
						VALUES (%s, %s, %s)
						""",
						(candidate_id, s.name.strip().lower(), s.experience),
					)
		return candidate_id
	finally:
		conn.close()
