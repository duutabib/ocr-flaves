import pdfplumber


def preprocess_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            return text
    