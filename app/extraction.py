from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from app.config import llm
from app.schemas import CandidateProfile, RawCandidateProfile
from app.skill_experience import resolve_skill_experience


structured_llm = llm.with_structured_output(RawCandidateProfile)

SYSTEM_PROMPT = """
Extract the candidate's profile from this resume text into the provided schema.

Rules:
- If a field is not present in the resume, leave it empty rather than inventing data.
- Work experience duration must be a number of years. Compute it from dates when necessary.
- Work experience skills must contain every skill or technology actually used in that role.
- stated_years must only contain an explicit number of years written for that skill in the resume. If no explicit number is present, use null.
- Do not calculate skill experience yourself.
- Normalize obvious casing and spelling variations to a consistent industry name and use the same normalized name in skills and work experience skill lists.
- Do not replace one technology with a related technology.
- Social fields must contain URLs only.
- Do not fabricate companies, schools, dates, skills, or contact information.

Resume:
{resume_text}
"""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def _extract_raw(resume_text: str) -> RawCandidateProfile:
    result = structured_llm.invoke(SYSTEM_PROMPT.format(resume_text=resume_text))
    if result is None:
        raise ValueError("Model returned no parsable profile.")
    return result


def extract_profile(resume_text: str) -> CandidateProfile:
    return resolve_skill_experience(_extract_raw(resume_text))
