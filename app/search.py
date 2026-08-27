from psycopg2.extras import RealDictCursor

from app.config import embeddings, llm
from app.db import get_connection
from app.query_parser import parse_search_query
from app.ranking import rank_candidates


VECTOR_TOP_K = 25


def retrieve_candidates(user_query: str, requirements, top_k: int = VECTOR_TOP_K) -> list[dict]:
    query_vector = embeddings.embed_query(user_query)
    filters = []
    params = [query_vector]

    if requirements.minimum_total_experience is not None:
        filters.append("c.total_experience_years >= %s")
        params.append(requirements.minimum_total_experience)

    if requirements.maximum_total_experience is not None:
        filters.append("c.total_experience_years <= %s")
        params.append(requirements.maximum_total_experience)

    if requirements.location:
        filters.append("c.address ILIKE %s")
        params.append(f"%{requirements.location}%")

    for skill_name, minimum_years in requirements.minimum_skill_experience.items():
        filters.append(
            "EXISTS ("
            "SELECT 1 FROM candidate_skills cs "
            "WHERE cs.candidate_id = c.id "
            "AND LOWER(cs.skill_name) = LOWER(%s) "
            "AND cs.experience >= %s"
            ")"
        )
        params.extend([skill_name, minimum_years])

    where_clause = ""
    if filters:
        where_clause = "WHERE " + " AND ".join(filters)

    sql = f"""
        SELECT
            c.id,
            c.name,
            c.email,
            c.phone_no,
            c.address,
            c.social,
            c.total_experience_years,
            c.work_experience,
            c.educations,
            c.skills,
            c.certificates,
            c.language,
            c.profile_summary,
            c.embedding <=> %s::vector AS distance
        FROM candidates c
        {where_clause}
        ORDER BY distance ASC
        LIMIT %s
    """

    params.append(top_k)
    conn = get_connection()

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def _profile_context(candidate: dict) -> str:
    skills = ", ".join(
        f"{skill['name']} ({skill['experience']} yrs)"
        for skill in candidate["skills"]
    ) or "none listed"

    jobs = "\n".join(
        f"- {job['company_name']} ({job['duration']} yrs): {job['summary']} "
        f"[skills: {', '.join(job['skills']) if job['skills'] else 'n/a'}]"
        for job in candidate["work_experience"]
    ) or "none listed"

    education = "\n".join(
        f"- {item['degree']} at {item['school']} ({item.get('duration') or 'n/a'})"
        for item in candidate["educations"]
    ) or "none listed"

    return (
        f"Candidate: {candidate['name']}\n"
        f"Total experience: {candidate['total_experience_years']} years\n"
        f"Location: {candidate['address'] or 'not specified'}\n"
        f"Skills: {skills}\n"
        f"Work experience:\n{jobs}\n"
        f"Education:\n{education}\n"
        f"Certificates: {', '.join(candidate['certificates']) if candidate['certificates'] else 'none listed'}\n"
        f"Languages: {', '.join(candidate['language']) if candidate['language'] else 'none listed'}"
    )


def generate_answer(user_query: str, requirements, candidates: list[dict]) -> str:
    if not candidates:
        return "No candidates satisfy the explicit requirements for this query."

    context = "\n\n".join(_profile_context(candidate) for candidate in candidates)

    prompt = f"""
You are a recruitment matching assistant.

Recruiter query:
{user_query}

Structured requirements:
{requirements.model_dump_json(indent=2)}

Candidate results:
{context}

Evaluate the candidates against the recruiter requirements.

Rules:
- Rank the candidates from strongest to weakest match.
- Explain the evidence for each important match.
- Distinguish total professional experience from skill-specific experience.
- Treat explicit structured requirements as requirements, not suggestions.
- Do not invent skills, experience, employers, dates, education, or technologies.
- Do not infer missing experience.
- If a requirement is not supported by the candidate data, say that it is not verified.
- If none is a strong match, say so clearly.
- Keep the answer concise and useful to a recruiter.
"""

    response = llm.invoke(prompt)
    return response.content


def search_candidates(user_query: str, top_k: int = 5) -> dict:
    if top_k < 1 or top_k > 50:
        raise ValueError("top_k must be between 1 and 50")

    requirements = parse_search_query(user_query)
    candidates = retrieve_candidates(user_query, requirements, VECTOR_TOP_K)
    ranked_candidates = rank_candidates(candidates, requirements)
    final_candidates = ranked_candidates[:top_k]
    answer = generate_answer(user_query, requirements, final_candidates)

    return {
        "answer": answer,
        "requirements": requirements.model_dump(),
        "matched_candidates": [
            {
                "id": candidate["id"],
                "name": candidate["name"],
                "email": candidate["email"],
                "phone_no": candidate["phone_no"],
                "address": candidate["address"],
                "total_experience_years": candidate["total_experience_years"],
                "skills": candidate["skills"],
                "work_experience": candidate["work_experience"],
                "educations": candidate["educations"],
                "certificates": candidate["certificates"],
                "language": candidate["language"],
                "similarity": round(max(0.0, 1.0 - float(candidate["distance"])), 4),
                "match_score": candidate["match_score"],
                "skill_match_score": candidate["skill_match_score"],
                "semantic_score": candidate["semantic_score"],
                "experience_match_score": candidate["experience_match_score"],
            }
            for candidate in final_candidates
        ],
    }
