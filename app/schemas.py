from pydantic import BaseModel, Field
from typing import List, Optional


class PersonalInfo(BaseModel):
	name: str = Field(description="Full name of the candidate")
	address: str = Field(default="", description="Candidate's location/address as written in the resume. Empty string if not found.")
	email: str = Field(default="", description="Candidate's email address. Empty string if not found.")
	phone_no: str = Field(
		default="",
		description="Candidate's phone number, exactly as written in the resume, including country "
		"code if present. Empty string if not found. Do not infer or guess a country code "
		"that is not explicitly stated.",
	)
	social: List[str] = Field(default_factory=list, description="Social/profile links: LinkedIn, GitHub, portfolio, etc.")


class WorkExperience(BaseModel):
	company_name: str
	duration: float = Field(description="Duration at this company, in years (e.g. 2.5). Compute from dates if given as a range.")
	skills: List[str] = Field(default_factory=list, description="Skills/technologies used in this specific role.")
	summary: str = Field(description="Roles & responsibilities summary for this role.")


class Education(BaseModel):
	school: str
	degree: str
	duration: Optional[str] = Field(default=None, description="e.g. '2015-2019' or '4 years'.")


class Skill(BaseModel):
	name: str
	experience: float = Field(
		default=0,
		description="Years of experience with this skill. If not explicitly stated, estimate from "
		"the work_experience entries where this skill appears; otherwise 0.",
	)


class CandidateProfile(BaseModel):
	personal_info: PersonalInfo
	work_experience: List[WorkExperience] = Field(default_factory=list)
	educations: List[Education] = Field(default_factory=list)
	skills: List[Skill] = Field(default_factory=list)
	certificates: List[str] = Field(default_factory=list)
	language: List[str] = Field(default_factory=list)


# --- Extraction-time schema ---------------------------------------------
# The LLM should NOT compute skill experience itself (LLMs are unreliable at
# arithmetic). Instead it reports only what's explicitly stated in the text
# (stated_years = null if the resume never gives a number for that skill).
# The actual years-of-experience-per-skill number is then computed
# deterministically in Python (see skill_experience.py):
#   1. if the resume explicitly states years for this skill -> use that
#   2. else -> sum the duration of every company where this skill was used
#   3. else (skill never appears in any job) -> 0
class RawSkill(BaseModel):
	name: str
	stated_years: Optional[float] = Field(
		default=None,
		description="Years of experience the resume EXPLICITLY states for this skill "
		"(e.g. 'Python (5 years)', '5+ years of React'). Null if no explicit number is "
		"given anywhere in the resume for this skill -- do NOT estimate or calculate "
		"this yourself, leave it null and it will be computed separately.",
	)


class RawCandidateProfile(BaseModel):
	personal_info: PersonalInfo
	work_experience: List[WorkExperience] = Field(default_factory=list)
	educations: List[Education] = Field(default_factory=list)
	skills: List[RawSkill] = Field(default_factory=list)
	certificates: List[str] = Field(default_factory=list)
	language: List[str] = Field(default_factory=list)
