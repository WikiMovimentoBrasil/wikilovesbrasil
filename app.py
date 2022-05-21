import yaml
import os
import json
import requests
from flask import Flask, render_template, request, redirect, session, url_for, jsonify, g, flash
from flask_babel import Babel, gettext
from oauth_wikidata import get_username, upload_file, get_token
from requests_oauthlib import OAuth1Session
from wikidata import query_monuments, query_monuments_without_coords, query_monument, get_category_info, get_article,\
    get_sitelinks, api_post_request
import gspread
from oauth2client.service_account import ServiceAccountCredentials

__dir__ = os.path.dirname(__file__)
app = Flask(__name__)
app.config.update(yaml.safe_load(open(os.path.join(__dir__, 'config.yaml'))))

BABEL = Babel(app)


##############################################################
# LOGIN
##############################################################
@app.before_request
def init_profile():
    g.profiling = []


@app.before_request
def global_user():
    g.user = get_username()


@app.route('/login')
def login():
    next_page = request.args.get('next')
    if next_page:
        session['after_login'] = next_page

    client_key = app.config['CONSUMER_KEY']
    client_secret = app.config['CONSUMER_SECRET']
    base_url = 'https://www.wikidata.org/w/index.php'
    request_token_url = base_url + '?title=Special%3aOAuth%2finitiate'

    oauth = OAuth1Session(client_key,
                          client_secret=client_secret,
                          callback_uri='oob')
    fetch_response = oauth.fetch_request_token(request_token_url)

    session['owner_key'] = fetch_response.get('oauth_token')
    session['owner_secret'] = fetch_response.get('oauth_token_secret')

    base_authorization_url = 'https://www.wikidata.org/wiki/Special:OAuth/authorize'
    authorization_url = oauth.authorization_url(base_authorization_url,
                                                oauth_consumer_key=client_key)
    return redirect(authorization_url)


@app.route("/oauth-callback", methods=["GET"])
def oauth_callback():
    base_url = 'https://www.wikidata.org/w/index.php'
    client_key = app.config['CONSUMER_KEY']
    client_secret = app.config['CONSUMER_SECRET']

    oauth = OAuth1Session(client_key,
                          client_secret=client_secret,
                          resource_owner_key=session['owner_key'],
                          resource_owner_secret=session['owner_secret'])

    oauth_response = oauth.parse_authorization_response(request.url)
    verifier = oauth_response.get('oauth_verifier')
    access_token_url = base_url + '?title=Special%3aOAuth%2ftoken'
    oauth = OAuth1Session(client_key,
                          client_secret=client_secret,
                          resource_owner_key=session['owner_key'],
                          resource_owner_secret=session['owner_secret'],
                          verifier=verifier)

    oauth_tokens = oauth.fetch_access_token(access_token_url)
    session['owner_key'] = oauth_tokens.get('oauth_token')
    session['owner_secret'] = oauth_tokens.get('oauth_token_secret')
    next_page = session.get('after_login')

    return redirect(next_page)


##############################################################
# LOCALIZAÇÃO
##############################################################
# Função para pegar a língua de preferência do usuário
@BABEL.localeselector
def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'pt')


# Função para mudar a língua de exibição do conteúdo
@app.route('/set_locale')
def set_locale():
    next_page = request.args.get('return_to')
    lang = request.args.get('lang')

    session["lang"] = lang
    redirected = redirect(next_page)
    redirected.delete_cookie('session', '/item')
    return redirected


def pt_to_ptbr(lang):
    if lang == "pt" or lang == "pt-br":
        return "pt-br"
    else:
        return lang


##############################################################
# PÁGINAS
##############################################################
# Página de erro
@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(406)
@app.errorhandler(408)
@app.errorhandler(409)
@app.errorhandler(410)
@app.errorhandler(411)
@app.errorhandler(412)
@app.errorhandler(413)
@app.errorhandler(414)
@app.errorhandler(415)
@app.errorhandler(416)
@app.errorhandler(417)
@app.errorhandler(418)
@app.errorhandler(422)
@app.errorhandler(423)
@app.errorhandler(424)
@app.errorhandler(429)
@app.errorhandler(500)
@app.errorhandler(501)
@app.errorhandler(502)
@app.errorhandler(503)
@app.errorhandler(504)
@app.errorhandler(505)
def page_not_found(e):
    username = get_username()
    lang = pt_to_ptbr(get_locale())
    return render_template('error.html',
                           username=username,
                           lang=lang,
                           error=e.original_exception.args[0])


# Função para exibir a tela de descrição do aplicativo
@app.route('/about')
@app.route('/sobre')
def sobre():
    username = get_username()
    lang = pt_to_ptbr(get_locale())
    return render_template('sobre.html',
                           username=username,
                           lang=lang)


# Página inicial
@app.route('/')
@app.route('/home')
@app.route('/inicio')
def inicio():
    username = get_username()
    lang = pt_to_ptbr(get_locale())
    return render_template('inicio.html',
                           username=username,
                           lang=lang)


@app.route('/mapa')
@app.route('/map')
def mapa():
    username = get_username()
    lang = pt_to_ptbr(get_locale())
    return render_template("map.html",
                           username=username,
                           lang=lang)


@app.route('/mapa/<uf>')
@app.route('/map/<uf>')
def mapa_uf(uf):
    username = get_username()
    lang = pt_to_ptbr(get_locale())
    states_qids = {"ac": "Q40780", "al": "Q40885", "am": "Q40040", "ap": "Q40130", "ba": "Q40430", "ce": "Q40123",
                   "df": "Q119158", "es": "Q43233", "go": "Q41587", "ma": "Q42362", "mg": "Q39109", "ms": "Q43319",
                   "mt": "Q42824", "pa": "Q39517", "pb": "Q38088", "pe": "Q40942", "pi": "Q42722", "pr": "Q15499",
                   "rj": "Q41428", "rn": "Q43255", "ro": "Q43235", "rr": "Q42508", "rs": "Q40030", "sc": "Q41115",
                   "se": "Q43783", "sp": "Q175", "to": "Q43695"}
    p18 = []
    p1766 = []
    p1801 = []
    p5775 = []
    p3451 = []
    p4291 = []
    p8592 = []
    p9721 = []

    monuments = query_monuments(states_qids[uf.lower()])
    qids_with_image = []
    qids_without_image = []
    comandos = "var "

    for item in monuments:
        tooltip = item["label"]
        tooltip_style = "{direction:'top', offset: [0, -37]}"
        popup = "<span style='text-align:center'><b>" + item["label"] + "</b></span><br><br>" + "<a class='custom-link' target='_blank' href='" + url_for("monumento", qid=item['item']) + "'><button class='send_button'><i class='fa-solid fa-arrow-up-from-bracket'></i> " + gettext("Enviar fotografia(s)") + "</div>"
        popup_style = "{closeButton: false}"
        if "imagem" in item and item["imagem"] != "No-image.png":
            if "p18" in item and item["p18"]:
                p18.append(item["item"])
            if "p1766" in item and item["p1766"]:
                p1766.append(item["item"])
            if "p1801" in item and item["p1801"]:
                p1801.append(item["item"])
            if "p5775" in item and item["p5775"]:
                p5775.append(item["item"])
            if "p3451" in item and item["p3451"]:
                p3451.append(item["item"])
            if "p4291" in item and item["p4291"]:
                p4291.append(item["item"])
            if "p8592" in item and item["p8592"]:
                p8592.append(item["item"])
            if "p9721" in item and item["p9721"]:
                p9721.append(item["item"])
            comandos += item["item"] + " = L.marker({lon: " + item["coord"][0] + ", lat: " + item["coord"][1] + "}, {icon: greenIcon})" + ".bindTooltip(\"" + tooltip + "\", " + tooltip_style + ").bindPopup(\"" + popup + "\", " + popup_style + "),\n"
            qids_with_image.append(item["item"])
        else:
            comandos += item["item"] + " = L.marker({lon: " + item["coord"][0] + ", lat: " + item["coord"][1] + "}, {icon: redIcon})" + ".bindTooltip(\"" + tooltip + "\", " + tooltip_style + ").bindPopup(\"" + popup + "\", " + popup_style + ").addTo(markers_without_image),\n"
            qids_without_image.append(item["item"])

        comandos = comandos[:-2] + ";\n"

    return render_template("map_uf.html",
                           markers=comandos,
                           markers_list="[" + ",".join(list(set(qids_without_image+qids_with_image))) + "]",
                           bounds=uf_bounds(uf),
                           P18="L.featureGroup.subGroup(markers_with_image, [" + ",".join(p18) + "]).addTo(map)",
                           P1766="L.featureGroup.subGroup(markers_with_image, ["+",".join(p1766)+"]).addTo(map)",
                           P1801="L.featureGroup.subGroup(markers_with_image, ["+",".join(p1801)+"]).addTo(map)",
                           P5775="L.featureGroup.subGroup(markers_with_image, ["+",".join(p5775)+"]).addTo(map)",
                           P3451="L.featureGroup.subGroup(markers_with_image, ["+",".join(p3451)+"]).addTo(map)",
                           P4291="L.featureGroup.subGroup(markers_with_image, ["+",".join(p4291)+"]).addTo(map)",
                           P8592="L.featureGroup.subGroup(markers_with_image, ["+",".join(p8592)+"]).addTo(map)",
                           P9721="L.featureGroup.subGroup(markers_with_image, ["+",".join(p9721)+"]).addTo(map)",
                           username=username,
                           lang=lang,
                           uf=uf)


@app.route('/mapa/<uf>/geolocalizar')
@app.route('/map/<uf>/geolocate')
def geolocate(uf):
    username = get_username()
    lang = pt_to_ptbr(get_locale())
    states_qids = {"ac": "Q40780", "al": "Q40885", "am": "Q40040", "ap": "Q40130", "ba": "Q40430", "ce": "Q40123",
                   "df": "Q119158", "es": "Q43233", "go": "Q41587", "ma": "Q42362", "mg": "Q39109", "ms": "Q43319",
                   "mt": "Q42824", "pa": "Q39517", "pb": "Q38088", "pe": "Q40942", "pi": "Q42722", "pr": "Q15499",
                   "rj": "Q41428", "rn": "Q43255", "ro": "Q43235", "rr": "Q42508", "rs": "Q40030", "sc": "Q41115",
                   "se": "Q43783", "sp": "Q175", "to": "Q43695"}

    monuments, locais = query_monuments_without_coords(states_qids[uf.lower()])

    return render_template("geolocate.html",
                           bounds=uf_bounds(uf),
                           monuments=monuments,
                           locais=locais,
                           username=username,
                           lang=lang,
                           uf=uf)


@app.route('/mapa/sugerir', methods=['GET', 'POST'])
@app.route('/map/suggest', methods=['GET', 'POST'])
def suggest():
    username = get_username()
    lang = pt_to_ptbr(get_locale())

    if request.method == "POST":
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(__dir__, 'credentials.json'), scope)
        client = gspread.authorize(creds)
        spreadsheet = app.config["SUGGESTIONS_SPREADSHEET"]
        gsheet = client.open(spreadsheet).sheet1

        name = request.form.get("inputName") or ""
        state = request.form.get("inputState") or ""
        local = request.form.get("inputLocal") or ""
        address = request.form.get("inputAddress") or ""
        url = request.form.get("inputURL") or ""
        comments = request.form.get("inputComments") or ""

        gsheet.append_row([name, state, local, address, url, comments])
        flash(gettext(u'Sua sugestão para adicionar %(val)s à lista de monumentos foi enviada com sucesso!', val=name))

    uf = request.args["uf"] if "uf" in request.args else ""

    return render_template("suggest.html",
                           username=username,
                           lang=lang,
                           uf=uf)


@app.route('/monumento/<qid>', methods=['GET', 'POST'])
@app.route('/monument/<qid>', methods=['GET', 'POST'])
def monumento(qid):
    username = get_username()
    lang = pt_to_ptbr(get_locale())

    if request.method == "POST":
        return send_file()
    else:
        metadata = query_monument(qid)
        if "commons_cat" in metadata:
            metadata["cat_info"] = get_category_info(metadata["commons_cat"][0])

        metadata["sitelinks"] = get_sitelinks(qid)
        aux_lang = "pt" if lang == "pt-br" else lang

        if aux_lang in metadata["sitelinks"]:
            metadata["article"] = get_article(aux_lang, metadata["sitelinks"][aux_lang])
            metadata["article_wiki"] = aux_lang
            metadata["article_name"] = metadata["sitelinks"][aux_lang]

        return render_template("item.html",
                               metadata=metadata,
                               username=username,
                               lang=lang)


##############################################################
# CONSULTAS E REQUISIÇÕES
##############################################################
@app.route('/postCoordinates', methods=['GET', 'POST'])
def post_coordinates():
    if request.method == "POST":
        jsondata = request.get_json()
        item = jsondata['item']
        lat = jsondata['lat']
        lon = jsondata['lon']
        username = get_username()
        token = get_token()

        params = {
            "action": "wbcreateclaim",
            "format": "json",
            "entity": item,
            "property": "P625",
            "snaktype": "value",
            "value": "{\"latitude\":" + str(lat) + ",\"longitude\":" + str(lon) + ",\"globe\":\"http://www.wikidata.org/entity/Q2\",\"precision\":0.000001}",
            "token": token,
        }

        result = api_post_request(params)

        return result.json(), 200


def uf_bounds(uf):
    bounds = {
        "ac": [[-7.11455, -73.9877], [-11.14079, -66.62477]],
        "al": [[-8.81351, -38.24062], [-10.495, -35.15274]],
        "am": [[2.21127, -73.79277], [-9.82285, -56.10689]],
        "ap": [[4.45595, -54.88245], [-1.23318, -49.85668]],
        "ba": [[-8.53291, -46.57167], [-18.33942, -37.35001]],
        "ce": [[-2.78442, -41.41907], [-7.85144, -37.25174]],
        "df": [[-15.50377, -48.29035], [-16.04661, -47.30901]],
        "es": [[-17.89285, -41.88207], [-21.30413, -28.85141]],
        "go": [[-12.41313, -53.25158], [-19.49416, -45.9171]],
        "ma": [[-1.05828, -48.73356], [-10.26398, -41.81136]],
        "mg": [[-14.23464, -51.04958], [-22.92105, -39.8653]],
        "ms": [[-17.21014, -58.17041], [-24.0668, -50.92176]],
        "mt": [[-7.3595, -61.64293], [-18.04229, -50.23019]],
        "pa": [[2.63347, -58.89861], [-9.84791, -46.06961]],
        "pb": [[-6.02229, -38.76881], [-8.29179, -34.78453]],
        "pe": [[0.91699, -41.35868], [-9.48159, -29.34511]],
        "pi": [[-2.7507, -46.04394], [-10.92968, -40.37564]],
        "pr": [[-22.52001, -54.62217], [-26.71808, -48.02367]],
        "rj": [[-20.76404, -44.89028], [-23.37064, -40.97376]],
        "rn": [[-4.82899, -38.58026], [-6.99202, -34.96684]],
        "ro": [[-7.97126, -66.80881], [-13.69538, -59.78473]],
        "rr": [[5.2828, -64.81748], [-1.53994, -58.90015]],
        "rs": [[-27.07847, -57.64831], [-33.75184, -49.71134]],
        "sc": [[-25.95592, -53.83147], [-29.35049, -48.35692]],
        "se": [[-9.51607, -38.24262], [-11.56879, -36.39707]],
        "sp": [[-19.77801, -53.11086], [-25.31153, -44.16265]],
        "to": [[-5.16349, -50.78033], [-13.46891, -45.70069]]
    }
    return bounds[uf.lower()]


def send_file():
    username = get_username()
    message = None

    if request.method == "POST":
        uploaded_files = request.files.getlist('files')
        form = request.form

        for file_ in uploaded_files:
            filename = file_.filename

            # Enviar imagem
            if username:
                data = upload_file(file_, filename, form)
                if "error" in data and data["error"]["code"] == "fileexists-shared-forbidden":
                    message = gettext(u"Uma imagem com este exato título já existe. Por favor, reformule o título.")
                elif "upload" in data and "warnings" in data["upload"] and "duplicate" in data["upload"]["warnings"]:
                    message = gettext(
                        u"Esta imagem é uma duplicata exata da imagem https://commons.wikimedia.org/wiki/File:%(file_)s",
                        file_=data["upload"]["warnings"]["duplicate"][0])
                elif "upload" in data and "warnings" in data["upload"] and "duplicate-archive" in data["upload"][
                    "warnings"]:
                    message = gettext(u"Esta imagem é uma duplicata exata de uma outra imagem que foi deletada da base.")
                elif "upload" in data and "warnings" in data["upload"] and "was-deleted" in data["upload"]["warnings"]:
                    message = gettext(
                        u"Uma outra imagem costumava utilizar este mesmo título. Por favor, reformule o título.")
                elif "upload" in data and "warnings" in data["upload"] and "exists" in data["upload"]["warnings"]:
                    message = gettext(u"Uma imagem com este exato título já existe. Por favor, reformule o título.")
                elif "error" in data:
                    message = data["error"]["code"]
                else:
                    message = gettext(
                        u"Imagem enviada com sucesso! Verifique suas contribuições clicando em seu nome de usuário(a).")
            else:
                message = gettext(
                    u'Ocorreu algum erro! Verifique o formulário e tente novamente. Caso o erro persista, por favor, reporte em https://github.com/WikiMovimentoBrasil/wikiusos/issues')
    return jsonify(message)


##############################################################
# MAIN
##############################################################
if __name__ == '__main__':
    app.run()
