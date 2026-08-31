import requests

LEETCODE_GRAPHQL = "https://leetcode.com/graphql"

def get_user_stats(username):
    query = """
    query getUserProfile($username: String!) {
        matchedUser(username: $username) {
            username
            submitStats: submitStatsGlobal {
                acSubmissionNum {
                    difficulty
                    count
                }
            }
            profile {
                ranking
            }
        }
    }
    """
    try:
        response = requests.post(
            LEETCODE_GRAPHQL,
            json={'query': query, 'variables': {'username': username}},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        data = response.json()
        user = data.get('data', {}).get('matchedUser')
        if not user:
            return None
        return user
    except Exception:
        return None


def get_problem(title_slug):
    query = """
    query getQuestion($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
            questionId
            title
            titleSlug
            content
            difficulty
            topicTags {
                name
            }
            exampleTestcases
            constraints: content
        }
    }
    """
    try:
        response = requests.post(
            LEETCODE_GRAPHQL,
            json={'query': query, 'variables': {'titleSlug': title_slug}},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        data = response.json()
        question = data.get('data', {}).get('question')
        if not question:
            return None

        examples = []
        if question.get('exampleTestcases'):
            examples = question['exampleTestcases'].split('\n')

        return {
            'questionId': question['questionId'],
            'title': question['title'],
            'titleSlug': question['titleSlug'],
            'content': question['content'],
            'difficulty': question['difficulty'],
            'topicTags': question.get('topicTags', []),
            'examples': examples
        }
    except Exception:
        return None