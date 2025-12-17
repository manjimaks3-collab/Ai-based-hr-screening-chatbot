import PyPDF2
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class ATSEngine:
    def __init__(self):
        pass

    def extract_text_from_pdf(self, file):
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return self.clean_text(text)
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""

    def clean_text(self, text):
        # Remove special characters and multiple spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.lower().strip()

    def calculate_compatibility_score(self, resume_text, job_description):
        if not resume_text or not job_description:
            return 0.0
            
        text = [resume_text, job_description]
        cv = CountVectorizer()
        count_matrix = cv.fit_transform(text)
        match_percentage = cosine_similarity(count_matrix)[0][1] * 100
        return round(match_percentage, 2)

    def check_keywords(self, resume_text, keywords):
        # Returns a list of missing keywords
        resume_text = resume_text.lower()
        missing = [kw for kw in keywords if kw.lower() not in resume_text]
        return missing
