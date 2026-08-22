from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from app.config import llm
from app.schemas import RawCandidateProfile, CandidateProfile
from app.skill_experience import resolve_skill_experience

structured_llm = llm.with_structured_output(RawCandidateProfile)

SYSTEM_PROMPT = """Extract the candidate's profile from this resume text into the given schema exactly.

Rules:
- If a field is not present in the resume, leave it empty/omit it rather than inventing data.
- work_experience[].duration must be a number of years (e.g. "Jan 2019 - Mar 2022" -> 3.2).
  If only start/end dates are given, compute the duration yourself.
- work_experience[].skills must list every skill/technology actually used in that specific role
  -- this matters, because years-of-experience-per-skill is calculated from these lists
  afterwards, not by you.
- skills[].stated_years: set this ONLY if the resume explicitly writes a number of years for
  that skill somewhere (e.g. "Python (5 years)", "5+ years of React", "AWS - 3 yrs"). If no such
  explicit number exists anywhere in the text for that skill, leave stated_years as null. Do NOT
  calculate, estimate, or infer a number yourself -- leave it null and it will be computed
  separately from the work_experience data.
- Normalize skill names to a consistent, common form (e.g. ".NET" not "dotnet" or "DotNet"), and
  use the SAME normalized name in both skills[] and every work_experience[].skills entry, so they
  can be matched up afterwards.
- personal_info.social should contain URLs only (LinkedIn, GitHub, portfolio, etc.).
- Do not fabricate companies, schools, or dates that are not present in the text.

Resume:
{resume_text}
"""


# gpt-5-mini (a reasoning model) has a known, intermittent failure mode with
# with_structured_output() where it returns malformed/incomplete JSON instead
# of a valid parse. Without a retry, one bad response fails the entire
# upload. Retrying 3x with a short backoff clears this in practice.
@retry(
	stop=stop_after_attempt(3),
	wait=wait_fixed(2),
	retry=retry_if_exception_type(Exception),
	reraise=True,
)
def _extract_raw(resume_text: str) -> RawCandidateProfile:
	prompt = SYSTEM_PROMPT.format(resume_text=resume_text)
	result = structured_llm.invoke(prompt)
	if result is None:
		raise ValueError("Model returned no parsable profile.")
	return result


def extract_profile(resume_text: str) -> CandidateProfile:
	"""Extracts raw facts via the LLM, then computes each skill's final years
	of experience deterministically in Python:
	  - explicit number stated in the resume -> use it
	  - else -> sum duration of every company where that skill was used
	  - else -> 0
	"""
	raw = _extract_raw(resume_text)
	return resolve_skill_experience(raw)
