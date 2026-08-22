from langchain_community.document_loaders import PyPDFLoader

# Below this many characters, the PDF almost certainly has no extractable
# text layer (i.e. it's a scanned image, not real text) -- PyPDFLoader
# cannot OCR, so we fail loudly here instead of silently handing the LLM
# an empty/near-empty string, which risks it inventing a profile from
# nothing despite the "don't invent information" instruction.
MIN_CHARS = 100


def load_resume_text(pdf_path: str) -> str:
	loader = PyPDFLoader(pdf_path)
	pages = loader.load()

	full_text = "\n".join(page.page_content for page in pages)

	if len(full_text.strip()) < MIN_CHARS:
		raise ValueError(
			"Could not extract readable text from this PDF -- it may be a "
			"scanned/image-only document. PyPDFLoader does not OCR scanned "
			"pages. Re-export the resume as a text-based PDF, or add an OCR "
			"fallback (e.g. pytesseract + pdf2image) for scanned files."
		)

	return full_text