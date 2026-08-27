from langchain_community.document_loaders import PyPDFLoader


MIN_CHARS = 100


def load_resume_text(pdf_path: str) -> str:
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    full_text = "\n".join(page.page_content for page in pages)

    if len(full_text.strip()) < MIN_CHARS:
        raise ValueError(
            "Could not extract readable text from this PDF. It may be scanned or image-only."
        )

    return full_text
