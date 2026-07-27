from pydantic import BaseModel, Field 
from typing import List, Optional

class CandidateProfiel(BaseModel):
	name: str = Field(description="Full name of the candidate")
	phone: str = Field(description="Candidate's Phone number,exactly as written in the resume, including country code if present. Empty string if not found.Do not infer or guess a country code that is not explicitly stated.)")
	email: str = Field(description="Candidate's email address, if present in the resume. Empty string if not found.")
	summary: str = Field(description="A comprehensive professional profile of the candidate covering their location, education, technical skills, soft skills, role titles/job history, years of experience, key projects, achievements, publications, and any other relevant details from the resume. Include everything from the resume that describes who the candidate is professionally — the more complete, the better. Do NOT include name, email, or phone number anywhere in this.")