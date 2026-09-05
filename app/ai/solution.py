from google import genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))


def generate_solution(problem, language):

    prompt = f"""
You are CodeHelp, an AI coding tutor.

Generate a correct solution for the following coding problem.

PROBLEM:
Title: {problem.title}
Difficulty: {problem.difficulty}
Platform: {problem.platform}

PROBLEM STATEMENT:
{problem.description}

TARGET LANGUAGE:
{language}

Return ONLY valid JSON. No markdown and no text outside the JSON.

{{
    "solution": "Complete solution code in {language}",
    "solution_explanation": "Plain-text explanation of the solution approach, why it works, and its time and space complexity. Do not use Markdown, LaTeX, mathematical delimiters such as $...$, backticks, HTML, or other formatting syntax."
}}

Requirements:
- The solution must correctly solve the problem.
- Write the complete solution in {language}.
- Do not use another programming language.
- Include compilable/complete code.
- Explain the reasoning clearly.
- Include time and space complexity.
- The solution_explanation must contain plain text only.
- Do not use Markdown or LaTeX formatting.
- Do not wrap complexity expressions in $...$.
- Write complexity as plain text, for example: O(N log N).
- Use simple numbered sections if helpful.
"""

    response = client.models.generate_content(
        model='gemini-3.5-flash-lite',
        contents=prompt
    )

    text = response.text.strip()

    if '```' in text:
        parts = text.split('```')

        for part in parts:
            if part.startswith('json'):
                text = part[4:].strip()
                break
            elif '{' in part:
                text = part.strip()
                break

    data = json.loads(text)

    data['solution'] = data.get('solution', '').replace('\\n', '\n')
    data['solution_explanation'] = data.get(
        'solution_explanation', ''
        ).replace('\\n', '\n')

    return data