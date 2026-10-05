import requests, time

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


_problemset_cache = None
_problemset_cache_time = 0
PROBLEMSET_CACHE_TTL = 3600  # 1 hour


def get_problem(contest_id, problem_index):
    global _problemset_cache, _problemset_cache_time

    try:
        now = time.time()

        # Reuse cached metadata for one hour.
        if (
            _problemset_cache is None
            or now - _problemset_cache_time >= PROBLEMSET_CACHE_TTL
        ):
            response = requests.get(
                "https://codeforces.com/api/problemset.problems",
                timeout=15
            )
            response.raise_for_status()

            data = response.json()

            if data.get('status') != 'OK':
                return None

            _problemset_cache = data.get(
                'result', {}
            ).get('problems', [])

            _problemset_cache_time = now

        for problem in _problemset_cache:
            if (
                problem.get('contestId') == int(contest_id)
                and problem.get('index', '').upper()
                == problem_index.upper()
            ):
                return {
                    'contest_id': problem['contestId'],
                    'index': problem['index'],
                    'name': problem['name'],
                    'rating': problem.get('rating'),
                    'tags': problem.get('tags', []),
                }

        return None

    except (requests.RequestException, ValueError, TypeError):
        return None