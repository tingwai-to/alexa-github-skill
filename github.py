import requests
from datetime import date
from dateutil.relativedelta import relativedelta
import json
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def convert_date(date_value):
    value = relativedelta()
    try:
        date_value = date_value.lower()
        table = {'day': relativedelta(days=1),
                 'week': relativedelta(weeks=1),
                 'month': relativedelta(months=1),
                 'year': relativedelta(years=1)}
        if date_value in table:
            value = table[date_value]
        else:
            value = relativedelta()
    except Exception as exc:
        logger.exception("Error converting date_value={0}"
                         .format(date_value))

    return value

def convert_language(language_value):
    value = 'null'
    try:
        language_value = language_value.lower()
        table = {'javascript': 'javascript',
                'java': 'java',
                 'python': 'python',
                 'css': 'css',
                 'php': 'php',
                 'ruby': 'ruby',
                 'c plus plus': 'c++',
                 'c': 'c',
                 'shell': 'shell',
                 'c sharp': 'c#',
                 'objective c': 'objective-c',
                 'r': 'r',
                 'vim l': 'viml',
                 'go': 'go',
                 'perl': 'perl',
                 'coffee script': 'coffeescript',
                 'tex': 'TeX',
                 'swift': 'swift',
                 'scala': 'scala',
                 'emacs lisp': 'emacslisp',
                 'haskell': 'haskell',
                 'lua': 'lua',
                 'clojure': 'clojure',
                 'matlab': 'matlab',
                 'arduino': 'arduino',
                 'make file': 'makefile',
                 'groovy': 'groovy',
                 'puppet': 'puppet',
                 'rust': 'rust',
                 'powershell': 'powershell',
                 'html': 'html',
                 'vba': 'vba',
                 'visual basic': 'visualbasic',
                 'delphi': 'delphi'}
        if language_value in table:
            value = table[language_value]
        else:
            value = 'null'  # is str for GET request
    except Exception as exc:
        logger.exception("Error converting language_value={0}"
                         .format(language_value))

    return value

def get_top_repo(date_value=None, language_value=None):
    N_REPOS = 5

    date_decrement = convert_date(date_value)
    language = convert_language(language_value)
    print(type(date_decrement), date_decrement, type(language), language)

    now = date.today()
    past = now - date_decrement
    past_str = past.strftime("%Y-%m-%d")

    # GET request using GitHub Search API
    url = 'https://api.github.com/search/repositories'
    headers = {'Accept': 'application/vnd.github.preview'}
    query = {'q': 'created:>={0} language:{1}'.format(past_str, language),
             'sort': 'stars',
             'order': 'desc'}
    r = requests.get(url, headers=headers, params=query)

    # response object to json
    data = json.loads(r.text)
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
        # str(i) because key must be str for session_attributes
        top_repos[str(i)] = filtered

    return top_repos, N_REPOS  # dict of dicts, int
