from psycopg2.extras import RealDictCursor
from app.db import get_connection
from app.config import embeddings, llm

def retrieve_candidates(user_query: str, top_k: int = 5):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    query_vector = embeddings.embed_query(user_query)
    
    sql = """
        SELECT id, name, email, phone, summary,
               embedding <=> %s::vector AS distance
        FROM candidates
        ORDER BY distance ASC
        LIMIT %s;
    """
    
    cur.execute(sql, [query_vector, top_k])
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    return results


def generate_answer(user_query: str, candidates: list[dict]) -> str:
    context = "\n\n".join([
        f"Candidate: {c['name']}\nProfile: {c['summary']}"
        for c in candidates
    ])
    
    prompt = f"""A recruiter is searching with this query: "{user_query}"

        Here are the retrieved candidate profiles:

        {context}

        Based on the candidates above, provide a helpful response to the recruiter's query. 
        Explain which candidate(s) best match and why, referencing specific skills/experience. 
        If none are a strong match, say so honestly.
        """
    response = llm.invoke(prompt)
    return response.content


def search_candidates(user_query: str, top_k: int = 5, max_distance: float=0.4):
    candidates = retrieve_candidates(user_query, top_k)
    answer = generate_answer(user_query, candidates)
    
    return {
        "answer": answer,
        "matched_candidates": [
            {
            "name": c["name"],
            "email": c["email"],
            "phone": c["phone"],
            "distance": c["distance"]
            } for c in candidates
        ]
    }