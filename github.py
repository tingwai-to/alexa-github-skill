from __future__ import print_function
import requests
from datetime import date
from dateutil.relativedelta import relativedelta
import json
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def convert_date(date_value):
    """
    Retrieves date decrement. Defaults to 1 day decrement if not specified.

    Args:
        date_value (str): see LIST_OF_TIME

    Returns:
        value (relativedelta):
    """
    value = relativedelta(days=1)
    try:
        date_value = date_value.lower()
        table = {'day': relativedelta(days=1),
                 'week': relativedelta(weeks=1),
                 'month': relativedelta(months=1),
                 'year': relativedelta(years=1)}
        if date_value in table:
            value = table[date_value]
        else:
            value = relativedelta(days=1)
    except Exception as exc:
        if date_value is not None:
            logger.exception("Error converting date_value={0}"
                             .format(date_value))

    return value

def convert_language(language_value):
    """
    Properly formats language for GitHub search.
    Defaults to 'null', same as all languages, 'if not specified.

    Args:
        language_value (str): see LIST_OF_PROGRAMMING_LANGUAGES

    Returns:
        value (str):
    """
    value = 'null'
    try:
        language_value = language_value.lower()
        table = {'javascript': 'JavaScript',
                 'java': 'Java',
                 'python': 'Python',
                 'css': 'CSS',
                 'php': 'PHP',
                 'ruby': 'Ruby',
                 'c plus plus': 'C++',
                 'c': 'C',
                 'shell': 'Shell',
                 'c sharp': 'C#',
                 'objective c': 'Objective-C',
                 'r': 'R',
                 'vim l': 'VimL',
                 'go': 'Go',
                 'perl': 'Perl',
                 'coffee script': 'CoffeeScript',
                 'tex': 'TeX',
                 'swift': 'Swift',
                 'scala': 'Scala',
                 'emacs lisp': 'EmacsLisp',
                 'haskell': 'Haskell',
                 'lua': 'Lua',
                 'clojure': 'Clojure',
                 'matlab': 'Matlab',
                 'arduino': 'Arduino',
                 'make file': 'Makefile',
                 'groovy': 'Groovy',
                 'puppet': 'Puppet',
                 'rust': 'Rust',
                 'powershell': 'Powershell',
                 'html': 'HTML'}
        if language_value in table:
            value = table[language_value]
        else:
            value = 'null'  # is str for GET request
    except Exception as exc:
        if language_value is not None:
            logger.exception("Error converting language_value={0}"
                         .format(language_value))

    return value

def get_top_repo(date_value=None, language_value=None):
    """
    Performs date calculation, GET request to GitHub Search API, and keeps
    specific repo data.

    Note:
        Amazon Alexa policy only permits content in languages supported by
        Alexa, currently English and German. A temporary workaround has been
        added to filter repos that contain non-ascii characters, obviously not a
        perfect solution. This will be fixed when a better lightweight solution
        is found.

    Args:
        date_value (str): optional argument of date
        language_value (str): optional argument of programming language

    Returns:
        top_repos (dict): repo data
            eg. {'0': {'description': description0,
                       'html_url': url0,
                       'language': language0,
                       'name': name0,
                       'watchers': int0},
                 '1': {'description': description1,
                       'html_url': url1,
                       'language': language1,
                       'name': name1,
                       'watchers': int1},
                 '#': {...}
                }
    """
    N_REPOS = 3

    date_decrement = convert_date(date_value)
    language = convert_language(language_value)
    print(date_value, date_decrement, language_value, language)

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
    data = data['items'][0:10]  # list of repos

    # filter specific keys, remove non-English repos per Alexa instructions
    counter = 0
    keys_keep = ['name', 'description', 'language', 'watchers', 'html_url']
    top_repos = {}  # dict used to store in session_attributes
    for repo in data:
        filtered = {}
        isEnglish = True

        for key in keys_keep:
            # remove non-ascii
            if isinstance(repo[key], unicode):
                remove_ascii = repo[key].encode('ascii', 'ignore')
                if repo[key] == remove_ascii:
                    filtered[key] = remove_ascii
                else:
                    isEnglish = False
                    break
            else:
                filtered[key] = repo[key]

        if isEnglish:
            top_repos[str(counter)] = filtered
            counter += 1

    return top_repos
