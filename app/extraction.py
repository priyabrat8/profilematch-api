from app.config import llm 
from app.schemas import CandidateProfiel

structured_llm = llm.with_structured_output(CandidateProfiel)

def extract_profile(resume_text: str) -> CandidateProfiel:
	prompt = f"""Extract the candidate's profile from this resume text.
	Be accurate, do not invent information that isn't present.
	Resume: {resume_text} """

	return structured_llm.invoke(prompt)