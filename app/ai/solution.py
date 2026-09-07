from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

SOLUTION_MODELS = [
    ('gemini-3.8-flash', 'high'),
    ('gemini-3.7-flash', 'high'),
    ('gemini-3.5-flash-lite', 'medium')
]


def build_solution_prompt(problem, language):
    return f"""
You are CodeHelp, an AI coding tutor responsible for generating the
final reference solution for a competitive programming problem.

Your primary requirement is CORRECTNESS.

Carefully reason through the problem before producing the final solution.

PROBLEM:
Title: {problem.title}
Difficulty: {problem.difficulty}
Platform: {problem.platform}

PROBLEM STATEMENT:
{problem.description}

CONSTRAINTS:
{json.dumps(problem.constraints, indent=2) if problem.constraints else "Not provided"}

EXAMPLES:
{json.dumps(problem.examples, indent=2) if problem.examples else "Not provided"}

TOPICS:
{json.dumps(problem.tags, indent=2) if problem.tags else "Not provided"}

TARGET LANGUAGE:
{language}

REQUIREMENTS:

1. Solve the exact problem described above.
2. Treat the provided constraints as authoritative.
3. Do not assume standard constraints for this problem.
4. Choose an algorithm appropriate for the actual constraints.
5. Carefully consider edge cases.
6. Verify that the implementation matches the algorithm.
7. The implementation must be complete and compilable in {language}.
8. Do not output pseudocode.
9. Do not output incomplete code.
10. Do not output alternative approaches.
11. Do not include debugging code.
12. Do not include TODOs.
13. Do not include abandoned reasoning or comments such as
    "wait", "actually", "let's rewrite", or "better approach".
14. Do not claim an optimization that is not present in the implementation.
15. The stated complexity must describe the actual implementation.
16. Mentally test the solution against important edge cases.
17. Do not change the problem requirements.

EXPLANATION REQUIREMENTS:

The solution_explanation must contain plain text only.

Do not use:
- Markdown
- LaTeX
- $...$
- backticks
- HTML
- mathematical formatting syntax

Write complexity in plain text, for example:

Time Complexity: O(N log N)
Space Complexity: O(N)

Use simple numbered sections if useful.

Return exactly:
- solution: complete final solution code
- solution_explanation: clear plain-text explanation including the
  approach, correctness reasoning, and actual time and space complexity.
"""


def generate_solution_with_model(problem, language, model, thinking_level):
    prompt = build_solution_prompt(problem, language)

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema={
                'type': 'OBJECT',
                'properties': {
                    'solution': {
                        'type': 'STRING'
                    },
                    'solution_explanation': {
                        'type': 'STRING'
                    }
                },
                'required': [
                    'solution',
                    'solution_explanation'
                ]
            },
            thinking_config=types.ThinkingConfig(
                thinking_level=thinking_level
            )
        )
    )

    data = json.loads(response.text)

    data['solution'] = data.get('solution', '').replace('\\n', '\n')
    data['solution_explanation'] = data.get(
        'solution_explanation', ''
    ).replace('\\n', '\n')

    return data


def generate_solution(problem, language):

    last_error = None

    for model, thinking_level in SOLUTION_MODELS:
        try:
            print(f"Trying solution model: {model}")

            return generate_solution_with_model(
                problem,
                language,
                model,
                thinking_level
            )

        except (ServerError, ClientError) as e:
            last_error = e

            print(
                f"Solution model failed: {model} -> {repr(e)}"
            )

            continue

        except json.JSONDecodeError as e:
            last_error = e

            print(
                f"Invalid structured response from: {model}"
            )

            continue

    raise RuntimeError(
        "All solution-generation models are currently unavailable."
    ) from last_error