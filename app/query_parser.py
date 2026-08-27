from typing import Optional

from pydantic import BaseModel, Field

from app.config import llm


class SearchRequirements(BaseModel):
    role: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    minimum_total_experience: Optional[float] = None
    maximum_total_experience: Optional[float] = None
    minimum_skill_experience: dict[str, float] = Field(default_factory=dict)
    location: Optional[str] = None
    other_requirements: list[str] = Field(default_factory=list)


QUERY_PARSER_PROMPT = """
You are a recruitment search query parser.

Convert the recruiter's natural-language request into structured search requirements.

Rules:
1. Extract technical skills, technologies, platforms, tools, frameworks, databases, languages, and other technical capabilities explicitly requested.
2. Do not use a predefined skill list and do not rely on hardcoded technology names.
3. Do not invent requirements.
4. Normalize obvious spelling/casing variations to a common industry name when the meaning is unambiguous, but never replace one technology with a related technology.
5. Extract minimum total professional experience when specified.
6. Extract maximum total professional experience when specified.
7. If experience is explicitly required for a particular skill, put the skill and minimum years in minimum_skill_experience.
8. Extract the requested role when present.
9. Extract location when present.
10. Put other explicit requirements that cannot be represented by the other fields into other_requirements.
11. If a field is not specified, return null or an empty collection.
12. Treat phrases such as '10+ years', 'at least 10 years', '10 years or more', and 'minimum 10 years' as minimum total experience when they refer to overall experience.
13. Preserve the meaning of the recruiter's request exactly.

Recruiter query:
{query}
"""


structured_llm = llm.with_structured_output(SearchRequirements)


def parse_search_query(query: str) -> SearchRequirements:
    result = structured_llm.invoke(QUERY_PARSER_PROMPT.format(query=query))
    if result is None:
        raise ValueError("The query parser returned no requirements.")
    return result
