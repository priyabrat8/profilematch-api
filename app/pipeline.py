from app.pdf_loader import load_resume_text
from app.extraction import extract_profile
from app.profile_summary import build_profile_summary
from app.config import embeddings
from app.db import insert_candidate


def process_resume(pdf_path: str):
	text = load_resume_text(pdf_path)

	# raw text -> full structured profile matching the original schema
	# (personal_info, work_experience[], educations[], skills[], certificates[], language[])
	profile = extract_profile(text)

	# build + embed a clean professional summary from the structured data
	profile_summary = build_profile_summary(profile)
	vector = embeddings.embed_query(profile_summary)

	# store the full structured profile, not a flattened version
	candidate_id = insert_candidate(profile, profile_summary, vector)

	print(f"Inserted candidate: {candidate_id}")
	return candidate_id
