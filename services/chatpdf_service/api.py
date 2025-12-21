from pypdf import PdfReader
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv
import os
load_dotenv()

client = OpenAI(api_key="YOUR_OPENAI_API_KEY")


def load_pdf_text(pdf_path: str) -> str:
    """Extract text from PDF"""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


# def chat_with_pdf(pdf_path: str, user_question: str) -> str:
#     pdf_text = load_pdf_text(pdf_path)

#     prompt = f"""
# You are an assistant that answers questions based ONLY on the provided PDF content.

# PDF Content:
# {pdf_text}

# Question:
# {user_question}

# Answer clearly and concisely.
# """

#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "You are a helpful PDF assistant."},
#             {"role": "user", "content": prompt},
#         ],
#         temperature=0.2,
#     )

#     return response.choices[0].message.content


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def chat_with_pdf(pdf_path: str, question: str) -> str:
    pdf_text = load_pdf_text(pdf_path)

    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
            You are an assistant that answers questions ONLY using the PDF content below.

            PDF Content:
            {pdf_text}

            User Question:
            {question}

            Answer clearly and concisely.
            """

    response = model.generate_content(prompt)
    return response.text