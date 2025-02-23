import PyPDF2
import io

def read_pdf(file_stream):
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_stream.read()))
        text = "\n".join([page.extract_text() for page in pdf_reader.pages])
        return text.strip() or "No readable text found in PDF"
    except Exception as e:
        raise RuntimeError(f"PDF processing failed: {str(e)}") from e