import requests
from datetime import datetime
from datetime import timedelta
import json


def get_top_repo():
    N_REPOS = 5

    # date of 1 week ago
    now = datetime.now()
    past = now - timedelta(weeks=1)
    past_str = past.strftime("%Y-%m-%d")  # str

    # GET request using GitHub Search API
    url = 'https://api.github.com/search/repositories'
    headers = {'Accept': 'application/vnd.github.preview'}
    query = {'q': 'created:>{}'.format(past_str),
             'sort': 'stars',
             'order': 'desc'}
    r = requests.get(url, headers=headers, params=query)

    # convert response object to json and get top N repos
    data = json.loads(r.text)  # dict
    data = data['items'][0:N_REPOS]  # list of repos

    # filter specific keys
    keys_keep = ['name', 'description', 'language', 'watchers', 'html_url']
    top_repos = {}  # dict used to store in session_attributes
    for i, repo in enumerate(data):
        filtered = {}
        for key in keys_keep:
            # remove non-ascii, Alexa can't pronounce foreign characters
            if isinstance(repo[key], unicode):
                filtered[key] = repo[key].encode('ascii', 'ignore')
            else:
                filtered[key] = repo[key]
        # str(i) because key must be type string for session_attributes
        top_repos[str(i)] = filtered

    return top_repos, N_REPOS  # dict of dicts
