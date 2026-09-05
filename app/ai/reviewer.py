from google import genai
from google.genai import types
import os
import json
from dotenv import load_dotenv
from app.ai.prompts import build_review_prompt

load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def review_attempt(problem, attempt, previous_review=None):
    prompt = build_review_prompt(problem, attempt, previous_review)

    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=prompt
        )
        text = response.text.strip()

        # Strip markdown code blocks if Gemini wraps in them
        if '```' in text:
            parts = text.split('```')
            for part in parts:
                if part.startswith('json'):
                    text = part[4:].strip()
                    break
                elif '{' in part:
                    text = part.strip()
                    break

        review_data = json.loads(text)
        return review_data

    except json.JSONDecodeError:
        return {
            'summary': 'Review generated but response was malformed. Please try again.',
            'correct': [],
            'issues': [],
            'complexity': {'time': 'O(?)', 'space': 'O(?)'},
            'think_about_this': None,
            'hints': [
                {'level': 1, 'type': 'conceptual', 'hint': None},
                {'level': 2, 'type': 'directional', 'hint': None},
                {'level': 3, 'type': 'specific', 'hint': None}
            ],
            'vs_previous': {'improvements': [], 'remaining_issues': []},
            'status': 'needs_work',
            'error': True
        }
    except Exception as e:
        print("GEMINI ERROR", repr(e))
        return {
            'summary': 'Review failed. Please try submitting again.',
            'correct': [],
            'issues': [],
            'complexity': {'time': 'O(?)', 'space': 'O(?)'},
            'think_about_this': None,
            'hints': [
                {'level': 1, 'type': 'conceptual', 'hint': None},
                {'level': 2, 'type': 'directional', 'hint': None},
                {'level': 3, 'type': 'specific', 'hint': None}
            ],
            'vs_previous': {'improvements': [], 'remaining_issues': []},
            'status': 'needs_work',
            'error': True
        }