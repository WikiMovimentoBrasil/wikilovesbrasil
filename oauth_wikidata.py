from flask import current_app, session
from requests_oauthlib import OAuth1Session
from urllib.parse import urlencode
from wikidata import query_wikidata
import os
import json
from datetime import date


project = "https://www.wikidata.org/w/api.php?"


def raw_request(params):
    app = current_app
    url = project + urlencode(params)
    client_key = app.config['CONSUMER_KEY']
    client_secret = app.config['CONSUMER_SECRET']
    oauth = OAuth1Session(client_key,
                          client_secret=client_secret,
                          resource_owner_key=session['owner_key'],
                          resource_owner_secret=session['owner_secret'])
    return oauth.get(url, timeout=4)


def raw_post_request(files, params, url_project=project):
    app = current_app
    url = url_project
    client_key = app.config['CONSUMER_KEY']
    client_secret = app.config['CONSUMER_SECRET']
    oauth = OAuth1Session(client_key,
                          client_secret=client_secret,
                          resource_owner_key=session['owner_key'],
                          resource_owner_secret=session['owner_secret'])
    if files:
        return oauth.post(url, files=files, data=params, timeout=4)
    else:
        return oauth.post(url, data=params, timeout=4)


def api_request(params):
    return raw_request(params).json()


def userinfo_call():
    params = {'action': 'query', 'meta': 'userinfo', 'format': 'json'}
    return api_request(params)


def get_username():
    if 'owner_key' not in session:
        return  # not authorized

    if 'username' in session:
        return session['username']

    reply = userinfo_call()
    if 'query' not in reply:
        return
    session['username'] = reply['query']['userinfo']['name']

    return session['username']


def get_token():
    params = {
        'action': 'query',
        'meta': 'tokens',
        'format': 'json',
        'formatversion': 2,
    }
    reply = api_request(params)
    token = reply['query']['tokens']['csrftoken']
    return token


def read_chunks(file_object, chunk_size=5000):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def upload_file(file, filename, form):
    token = get_token()

    chunks = read_chunks(file)
    chunk = next(chunks)

    files_dict = {}
    for i in range(int(form.__len__()/2)):
        files_dict[form["filename_"+str(i)]] = form["suggestedfilename_" + str(i)]

    file_ext = get_file_ext(filename)
    params = {
        "action": "upload",
        "stash": 1,
        "filename": files_dict[filename]+file_ext,
        "offset": 0,
        "format": "json",
        "token": token,
        "ignorewarnings": 1
    }

    index = 0
    file = {'chunk': (('{}.' + file_ext).format(index), chunk, 'multipart/form-data')}
    index += 1
    res = raw_post_request(file, params, "https://commons.wikimedia.org/w/api.php?")
    data = res.json()

    for chunk in chunks:
        params = {
            "action": "upload",
            "stash": 1,
            "filename": files_dict[filename]+file_ext,
            "filekey": data["upload"]["filekey"],
            "offset": data["upload"]["offset"],
            "format": "json",
            "token": token,
            "ignorewarnings": 1
        }
        file = {'chunk': (('{}.' + file_ext).format(index), chunk, 'multipart/form-data')}
        index += 1
        res = raw_post_request(file, params)
        data = res.json()

    params = {
        "action": "upload",
        "filename": files_dict[filename] + file_ext,
        "filekey": data["upload"]["filekey"],
        "format": "json",
        "token": token,
        "comment": "Uploaded using Wiki Loves Brasil",
        "text": build_text()
    }

    res = raw_post_request("", params)
    data = res.json()

    return data


def build_text(qid, timestamp):
    result = query_wikidata("SELECT DISTINCT ?item ?itemDescription ?name ?local ?localLabel "
                            "?local_cat ?estado ?estadoLabel (LANG(?itemDescription) AS ?lang) "
                            "WHERE { "
                            "BIND(wd:" + qid + " AS ?item) "
                            "OPTIONAL { [] schema:about ?item; "
                            "schema:isPartOf <https://commons.wikimedia.org/>; "
                            "schema:name ?name. } "
                            "{ ?item p:P131/ps:P131 ?local. } UNION { ?item p:P131/ps:P131 [wdt:P131 ?local]. } "
                            "{ ?local wdt:P31 wd:Q3184121 } UNION { ?local wdt:P31 wd:Q515 } "
                            "?local wdt:P131 ?estado. "
                            "?estado wdt:P31 wd:Q485258. "
                            "OPTIONAL { ?local wdt:P373 ?local_cat. } "
                            "SERVICE wikibase:label { bd:serviceParam wikibase:language 'pt-br,pt,en'. }}")

    lang = ""
    descr = ""
    year = str(date.today().year)
    username = "Eder" #get_username()

    category_local = ""
    category_monument = ""
    category_tool = "Uploaded via Wiki Loves Brasil"

    local_ = ""
    state_ = ""

    if "bindings" in result["results"] and result["results"]["bindings"]:
        for item in result["results"]["bindings"]:
            lang = item["lang"]["value"] if "lang" in item else "pt"
            descr = item["itemDescription"]["value"] if "itemDescription" in item and item["itemDescription"]["value"] else "fotografia de bem tombado em " + item["localLabel"]["value"] + ", " + item["estadoLabel"]["value"] + "."
            category_monument = item["name"]["value"] if "name" in item else ""
            category_local = item["local_cat"]["value"] if "local_cat" in item else ""
            local_ = item["local"]["value"].replace("http://www.wikidata.org/entity/", "") if "local" in item else ""
            state_ = item["estado"]["value"].replace("http://www.wikidata.org/entity/", "") if "estado" in item else ""

    with open(os.path.join(current_app.static_folder, 'categories' + year + '.json'), encoding="utf-8") as cat_list:
        contest_cats = json.load(cat_list)
    if local_ in contest_cats["cidades"]:
        category_wlm = contest_cats["cidades"][local_]
    elif state_ in contest_cats["estados"]:
        category_wlm = contest_cats["estados"][state_]
    else:
        category_wlm = "Images from Wiki Loves Monuments " + year + " in Brazil without proper category"

    if category_monument:
        category_local = ""

    categories = list(filter(None, [category_monument, category_local, category_wlm, category_tool]))

    text = ("=={{int:filedesc}}==\n" +
            "{{Information\n" +
            "|description={{" + lang + "|1=" + descr + "}}\n{{MonumentID|" + qid + "}}\n" +
            "|date=" + str(timestamp) + "\n" +
            "|source={{own}}\n" +
            "|author=[[User:" + username + "|" + username + "]]\n" +
            "}}\n\n" +
            "=={{int:license-header}}==\n" +
            "{{self|cc-by-sa-4.0}}\n{{Wiki Loves Monuments " + year + "|br}}\n\n" +
            "[[" + "]]\n[[Category:".join(categories) + "]]" +
            "[[Category:Uploaded via WikiLovesBrasil|" + qid + "]]\n")
    return text


def get_license(license_):
    if license_ == "ccbysa3":
        return "Cc-by-sa-3.0"
    elif license_ == "ccby4":
        return "Cc-by-4.0"
    elif license_ == "ccby3":
        return "Cc-by-3.0"
    elif license_ == "cc0":
        return "Cc-zero"
    else:
        return "Cc-by-sa-4.0"


def get_file_ext(filename):
    file_ext = filename.split(".")[-1]
    if file_ext != filename:
        return "." + file_ext
    return ""
