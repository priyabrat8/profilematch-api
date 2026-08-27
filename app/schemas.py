from pydantic import BaseModel, Field
from typing import List, Optional


class PersonalInfo(BaseModel):
    name: str = Field(description="Full name of the candidate")
    address: str = Field(default="", description="Candidate's location/address as written in the resume. Empty string if not found.")
    email: str = Field(default="", description="Candidate's email address. Empty string if not found.")
    phone_no: str = Field(default="", description="Candidate's phone number exactly as written in the resume. Empty string if not found.")
    social: List[str] = Field(default_factory=list, description="Social/profile links such as LinkedIn, GitHub, or portfolio URLs.")


class WorkExperience(BaseModel):
    company_name: str
    duration: float = Field(description="Duration at this company in years.")
    skills: List[str] = Field(default_factory=list, description="Skills and technologies used in this specific role.")
    summary: str = Field(description="Roles and responsibilities summary for this role.")


class Education(BaseModel):
    school: str
    degree: str
    duration: Optional[str] = Field(default=None, description="Education period or duration when present.")


class Skill(BaseModel):
    name: str
    experience: float = Field(default=0, description="Years of experience with this skill.")


class CandidateProfile(BaseModel):
    personal_info: PersonalInfo
    work_experience: List[WorkExperience] = Field(default_factory=list)
    educations: List[Education] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)
    certificates: List[str] = Field(default_factory=list)
    language: List[str] = Field(default_factory=list)


class RawSkill(BaseModel):
    name: str
    stated_years: Optional[float] = Field(default=None, description="Years of experience explicitly stated for this skill in the resume, otherwise null.")


class RawCandidateProfile(BaseModel):
    personal_info: PersonalInfo
    work_experience: List[WorkExperience] = Field(default_factory=list)
    educations: List[Education] = Field(default_factory=list)
    skills: List[RawSkill] = Field(default_factory=list)
    certificates: List[str] = Field(default_factory=list)
    language: List[str] = Field(default_factory=list)
