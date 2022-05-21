from flask import current_app, session
from requests_oauthlib import OAuth1Session
from urllib.parse import urlencode
from flask_babel import gettext

project = "https://test.wikidata.org/w/api.php"


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


def raw_post_request(files, params):
    app = current_app
    url = project
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
    res = raw_post_request(file, params)
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
        "comment": "Uploaded using Wiki Loves Brasil"
    }

    res = raw_post_request("", params)
    data = res.json()

    return data


def build_text(form, username):
    descr = gettext(u"Imagem contribuída através do aplicativo ''Wiki Museu do Ipiranga - Para que serve?''")

    if "para_que_serve" in form and form["para_que_serve"]:
        descr = descr + " Para que serve: \"" + form["para_que_serve"] + "\""

    text = ("=={{int:filedesc}}==\n"
            "{{Information\n"
            "|description={{"+form["lang"]+"|1="+descr+"}}\n"
            "|date="+form["date"]+"\n"
            "|source={{own}}\n"
            "|author=[[User:"+username+"|"+username+"]]\n"
            "|other fields = {{Wikiusos/Information field|qid = "+form["qid"]+"}}\n"
            "}}\n\n"
            "=={{int:license-header}}==\n"
            "{{Wikiusos}}\n"
            "{{"+get_license(form["license"])+"}}\n\n"
            "[[Category:Uploaded with wikiusos|"+form["qid"]+"]]"
            )
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


def add_p625(item, lat, lon):
    app = current_app
    params = {
        "action": "wbcreateclaim",
        "entity": item,
        "property": "P625",
        "snaktype":"value",
        "value": {
            "latitude":float(lat),
            "longitude":float(lon),
            "globe":"http://www.wikidata.org/entity/Q2",
            "precision": 0.000001
        }
    }
    url = "https://www.wikidata.org/w/api.php"
    client_key = app.config['CONSUMER_KEY']
    client_secret = app.config['CONSUMER_SECRET']
    oauth = OAuth1Session(client_key,
                          client_secret=client_secret,
                          resource_owner_key=session['owner_key'],
                          resource_owner_secret=session['owner_secret'])
    return oauth.get(url, params=params, timeout=4)