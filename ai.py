import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-3.5-flash")


def analyse_resume(resume_text,user_goal):
    prompt = f"""You are a senior software and hiring manager.
evaluate the resume based on the users goal.
User goal: "{user_goal}"

Strict Rules:
-Extract relevant skills for this goal
-Remove irrelevant tools
-Identify real gaps
-Generate a roadmap only for missing fields
-Make output DIFFERENT based on the user goal

Return only JSON:
{{
    "skills": [],
    "missing_skills": [],
    "roadmap": [],
    "interview_questions": []
}}
Resume:
{resume_text}

"""

    try:
        response = model.generate_content(prompt)

        text = response.text.replace("```json","").replace("```","").strip()

        return json.loads(text)

    except Exception as e:
        return {
            "skills":[],
            "missing_skills":[],
            "roadmap":[],
            "interview_questions":[],
            "error":str(e)
    }



