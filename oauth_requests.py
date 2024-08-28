from flask import current_app, session
from requests_oauthlib import OAuth1Session
from urllib.parse import urlencode


# ==================================================================================================================== #
# REQUISIÇÕES GET
# ==================================================================================================================== #
def raw_request(params, url_project):
    app = current_app
    url = url_project
    client_key = app.config['CONSUMER_KEY']
    client_secret = app.config['CONSUMER_SECRET']
    oauth = OAuth1Session(client_key,
                          client_secret=client_secret,
                          resource_owner_key=session['owner_key'],
                          resource_owner_secret=session['owner_secret'])
    return oauth.get(url, params=params, timeout=60)


def api_request(params, url_project):
    return raw_request(params, url_project).json()


# ----- INFORMAÇÕES SOBRE O USUÁRIO ----- #
def get_username(url_project):
    if 'owner_key' not in session:
        return  # not authorized

    if 'username' in session:
        return session['username']

    params = {'action': 'query', 'meta': 'userinfo', 'format': 'json'}
    reply = api_request(params, url_project)

    if 'query' not in reply:
        return

    session['username'] = reply['query']['userinfo']['name']

    return session['username']


def get_token(url_project):
    params = {
        'action': 'query',
        'meta': 'tokens',
        'format': 'json',
        'formatversion': 2,
    }
    reply = api_request(params, url_project)
    token = reply['query']['tokens']['csrftoken']
    return token


# ==================================================================================================================== #
# REQUISIÇÕES POST
# ==================================================================================================================== #
def raw_post_request(files, params, url_project):
    app = current_app
    url = url_project
    client_key = app.config['CONSUMER_KEY']
    client_secret = app.config['CONSUMER_SECRET']
    oauth = OAuth1Session(client_key,
                          client_secret=client_secret,
                          resource_owner_key=session['owner_key'],
                          resource_owner_secret=session['owner_secret'])
    if files:
        return oauth.post(url, files=files, data=params, timeout=60)
    else:
        return oauth.post(url, data=params, timeout=60)
