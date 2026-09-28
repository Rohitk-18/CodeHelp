import requests

CODEFORCES_API = "https://codeforces.com/api/user.info"


def get_user_profile(username):
    try:
        response = requests.get(
            CODEFORCES_API,
            params={'handles': username},
            timeout=10
        )

        data = response.json()

        if data.get('status') != 'OK':
            return None

        users = data.get('result', [])

        if not users:
            return None

        return users[0]

    except Exception:
        return None

def get_codeforces_stats(username):
    profile = get_user_profile(username)

    if not profile:
        return None

    return {
        'username': profile.get('handle'),
        'rating': profile.get('rating'),
        'rank': profile.get('rank'),
        'max_rating': profile.get('maxRating'),
        'max_rank': profile.get('maxRank')
    }