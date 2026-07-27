from langchain_community.document_loaders import PyPDFLoader

def load_resume_text(pdf_path: str) -> str:
	loader = PyPDFLoader(pdf_path)
	pages = loader.load()

	full_text = "\n".join(page.page_content for page in pages)
	return full_text