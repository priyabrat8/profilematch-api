import json
from psycopg2.extras import RealDictCursor
from app.db import get_connection
from app.config import embeddings, llm


def retrieve_candidates(user_query: str, top_k: int = 5, max_distance: float = 0.4):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query_vector = embeddings.embed_query(user_query)

            sql = """
                SELECT id, name, email, phone_no, address, total_experience_years,
                       work_experience, educations, skills, certificates, language,
                       profile_summary,
                       embedding <=> %s::vector AS distance
                FROM candidates
                WHERE (embedding <=> %s::vector) <= %s
                ORDER BY distance ASC
                LIMIT %s;
            """
            cur.execute(sql, [query_vector, query_vector, max_distance, top_k])
            return cur.fetchall()
    finally:
        conn.close()


def _profile_context(c: dict) -> str:
    """Renders one candidate's FULL structured profile as text for the LLM
    to ground its answer in -- actual work history/skills, not a one-line
    summary -- so the explanation can cite specifics (which job, which skill)."""
    skills = ", ".join(f"{s['name']} ({s['experience']} yrs)" for s in c["skills"]) or "none listed"
    jobs = "\n".join(
        f"  - {j['company_name']} ({j['duration']} yrs): {j['summary']} "
        f"[skills: {', '.join(j['skills']) if j['skills'] else 'n/a'}]"
        for j in c["work_experience"]
    ) or "  none listed"
    education = "\n".join(
        f"  - {e['degree']} at {e['school']} ({e.get('duration') or 'n/a'})"
        for e in c["educations"]
    ) or "  none listed"

    return (
        f"Candidate: {c['name']}\n"
        f"Total experience: {c['total_experience_years']} years\n"
        f"Location: {c['address'] or 'not specified'}\n"
        f"Skills: {skills}\n"
        f"Work experience:\n{jobs}\n"
        f"Education:\n{education}"
    )


def generate_answer(user_query: str, candidates: list[dict]) -> str:
    if not candidates:
        return (
            "No candidates in the database are a reasonable match for this query. "
            "Try broadening the search or check that relevant resumes have been uploaded."
        )

    context = "\n\n".join(_profile_context(c) for c in candidates)

    prompt = f"""A recruiter is searching with this query: "{user_query}"

        Here are the retrieved candidate profiles (full structured data, not just a summary):

        {context}

        Based on the candidates above, provide a helpful response to the recruiter's query.
        Explain which candidate(s) best match and why, referencing specific companies, skills,
        and years of experience from the data above. If none are a strong match, say so honestly.
        Do not invent details not present above.
        """
    response = llm.invoke(prompt)
    return response.content


def search_candidates(user_query: str, top_k: int = 5, max_distance: float = 0.4):
    candidates = retrieve_candidates(user_query, top_k, max_distance)
    answer = generate_answer(user_query, candidates)

    return {
        "answer": answer,
        "matched_candidates": [
            {
                "name": c["name"],
                "email": c["email"],
                "phone_no": c["phone_no"],
                "address": c["address"],
                "total_experience_years": c["total_experience_years"],
                "skills": c["skills"],
                "work_experience": c["work_experience"],
                "educations": c["educations"],
                "certificates": c["certificates"],
                "language": c["language"],
                "similarity": round(1 - c["distance"], 3),
            }
            for c in candidates
        ],
    }
