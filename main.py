from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
import shutil
import os
import uuid

from app.pipeline import process_resume
from app.search import search_candidates

app = FastAPI(title="ProfileMatch API")

UPLOAD_DIR = "resume"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE = 5 * 1024 *1024

@app.get("/")
async def root():
	return {"message": "ProfileMatch API is running"}

@app.get("/help")
async def help_endpoint():
    return {
        "message": "Welcome to ProfielMatch API",
        "endpoints": {
            "GET /": "Health check ",
            "POST /upload-resume": "Upload a PDF resume.",
            "GET /search": "Search for candidates using a natural-language query. Query param: 'query' (required), 'top_k' (optional, default 5).",
            "GET /help": "Shows help message"
        },
        "example_search": "/search?query=Find a Python developer in London&top_k=5"
    }


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Page not found",
            "message": f"The route '{request.url.path}' does not exist.",
            "hint": "Visit /help to see available endpoints, or /docs for interactive API documentation."
        }
    )

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
	if not file.filename.endswith(".pdf"):
		raise HTTPException(status_code=400, detail="File is not a valid PDF")

	header = await file.read(4)
	await file.seek(0)

	if header != b"%PDF":
		raise HTTPException(status_code=400, detail="File is not a valid PDF")

	content = await file.read()
	if len(content) > MAX_FILE_SIZE:
		raise HTTPException(status_code=400, detail="File too large (max 5MB)")

	safe_filename = f"{uuid.uuid4().hex}.pdf"
	file_path = os.path.join(UPLOAD_DIR, safe_filename)
	with open(file_path, "wb") as buffer:
		buffer.write(content)

	try:
		candidate_id = process_resume(file_path)
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))
	finally:
		if os.path.exists(file_path):
			os.remove(file_path)

	return {"message": "Resume processed successfully", "candidate_id": candidate_id}

@app.get("/search")
async def search(query: str, top_k: int = 5, max_distance: float = 0.4):
	try:
		result = search_candidates(query, top_k=top_k, max_distance=max_distance)
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

	return result