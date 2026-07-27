from app.pdf_loader import load_resume_text
from app.extraction import extract_profile
from app.config import embeddings
from app.db import insert_candidate

def process_resume(pdf_path: str):
	text = load_resume_text(pdf_path)
	profile = extract_profile(text)
	profile_dict = profile.model_dump()
	vector = embeddings.embed_query(profile_dict["summary"])
	candidate_id = insert_candidate(profile_dict,vector)

	print(f"Inserted candidate: {candidate_id}")
	return candidate_id