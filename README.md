# ProfileMatch API

A resume search system built with LangChain and RAG. Upload PDF resumes, then search for candidates using natural language queries instead of exact keyword or filter matching. The system retrieves semantically relevant profiles and uses an LLM to generate an explanation of how well each candidate matches the query.

Example query: `Find a Python developer with cloud infrastructure experience`

---

## What it does

1. 📄 Upload a PDF resume
2. 🤖 AI extracts and understands the candidate's profile
3. 🔎 Search in plain English : no filters, no keywords
4. ✅ Get back matched candidates **with an explanation**, not just a list

---

## Demo

**Query:** `Find someone who knows Python and cloud infrastructure`

**Response:**
> Ankit Kumar is the strongest match: deep AWS, Kubernetes, and Terraform experience, with Python used for infrastructure automation. Jason O'Brien is a partial match with some Python and internship-level cloud exposure. Brianna Stewart's background is in music production and isn't a fit here.

---

## Stack

`LangChain` · `OpenAI (GPT-5 mini + embeddings)` · `PostgreSQL + pgvector` · `FastAPI`

---

## Quick Start

**1. Install dependencies**
```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

**2. Set up environment variables**

Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_key
DB_NAME=resume_rag
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

**3. Create the database table**
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE candidates (
    id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT,
    phone TEXT,
    summary TEXT,
    embedding vector(1536)
);
```

**4. Run the API**
```bash
uvicorn main:app --reload
```

**5. Try it out**

Open `http://127.0.0.1:8000/docs` in your browser.

---

## API

| Endpoint | What it does |
|---|---|
| `POST /upload-resume` | Upload a PDF, it gets processed and stored |
| `GET /search?query=...` | Search candidates in plain English |

---


## Notes

- Contact info (name, email, phone) is stored separately from the embedded profile text — it never gets baked into the vector.
- Built with synthetic/sample resumes. Real candidate data in production would need encryption, access control, and consent.

---

## License

MIT — see [LICENSE](LICENSE).
