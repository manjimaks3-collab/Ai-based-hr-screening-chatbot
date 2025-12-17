import os
import google.generativeai as genai
import json
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure API
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def evaluate_screening_chat(chat_history, job_description):
    """
    Evaluates a candidate's screening chat transcript.
    Returns a score (0-100) and a brief summary.
    """
    if not api_key or "YOUR_GEMINI_API_KEY" in api_key:
        logging.warning("No Google API Key found. Returning mock score.")
        return 75, "AI Scoring disabled (No API Key)."

    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Prepare Prompt
        transcript_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
        
        prompt = f"""
        You are an Expert HR Recruiter. Evaluate the following candidate screening chat for the Job Description provided.
        
        Job Description:
        {job_description}
        
        Chat Transcript:
        {transcript_text}
        
        Task:
        1. Analyze the candidate's communication skills, relevance of answers, and professionalism.
        2. Provide a Screening Score from 0 to 100.
        3. Provide a 1-sentence summary justification.
        
        Output JSON format only:
        {{
            "score": <int>,
            "summary": "<string>"
        }}
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean markdown if present
        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "")
            
        result = json.loads(text)
        return result.get('score', 50), result.get('summary', 'Analyzed by AI.')
        
    except Exception as e:
        logging.error(f"AI Scoring Failed: {e}")
        return 50, f"Error during AI analysis: {str(e)}"
