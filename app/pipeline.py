from app.config import embeddings
from app.db import insert_candidate
from app.extraction import extract_profile
from app.pdf_loader import load_resume_text
from app.profile_summary import build_profile_summary


def process_resume(pdf_path: str):
    text = load_resume_text(pdf_path)
    profile = extract_profile(text)
    profile_summary = build_profile_summary(profile)
    vector = embeddings.embed_query(profile_summary)
    return insert_candidate(profile, profile_summary, vector)
