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
        return data.get('data', {}).get('question')
    except Exception:
        return None