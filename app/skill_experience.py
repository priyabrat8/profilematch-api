from app.schemas import RawCandidateProfile, CandidateProfile, Skill


def resolve_skill_experience(raw: RawCandidateProfile) -> CandidateProfile:
	"""Computes the final years-of-experience for each skill:

	  1. If the resume explicitly stated a number for this skill -> use it.
	  2. Else -> sum the duration of every company in work_experience whose
	     skills list includes this skill (case-insensitive, trimmed).
	  3. Else (skill never mentioned in any job, no explicit number) -> 0.

	Doing this in Python instead of asking the LLM to compute it removes the
	risk of arithmetic mistakes -- the LLM only has to report what's
	literally written in the text (stated_years) and list which skills were
	used at which job; the summing is exact.
	"""

	years_by_skill_from_jobs: dict[str, float] = {}
	for job in raw.work_experience:
		for skill_name in job.skills:
			key = skill_name.strip().lower()
			years_by_skill_from_jobs[key] = years_by_skill_from_jobs.get(key, 0.0) + job.duration

	resolved_skills: list[Skill] = []
	for raw_skill in raw.skills:
		key = raw_skill.name.strip().lower()

		if raw_skill.stated_years is not None:
			experience = raw_skill.stated_years
		elif key in years_by_skill_from_jobs:
			experience = round(years_by_skill_from_jobs[key], 1)
		else:
			experience = 0.0

		resolved_skills.append(Skill(name=raw_skill.name, experience=experience))

	return CandidateProfile(
		personal_info=raw.personal_info,
		work_experience=raw.work_experience,
		educations=raw.educations,
		skills=resolved_skills,
		certificates=raw.certificates,
		language=raw.language,
	)
