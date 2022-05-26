import requests
import os
from flask import current_app, session, url_for
from requests_oauthlib import OAuth1Session
from urllib.parse import unquote


def query_wikidata(query):
    url = "https://query.wikidata.org/sparql"
    params = {
        "query": query,
        "format": "json"
    }
    result = requests.get(url=url, params=params, headers={'User-agent': 'WLM Brasil'})
    data = result.json()
    return data


def query_monuments(qid, lang):
    result = query_wikidata("SELECT DISTINCT ?item ?itemLabel ?local ?localLabel ?coord "
                            "?P18 ?P3311 ?P4291 ?P4640 ?P8517 ?P1442 ?P1766"
                            "?P1801 ?P3451 ?P5252 ?P5775 ?P8592 ?P9721 ?P9906 "
                            "WITH { "
                            "SELECT DISTINCT ?item WHERE { ?item wdt:P131* wd:" + qid +
                            "; wdt:P1435 []. } "
                            "} AS %items "
                            "WHERE { "
                            "INCLUDE %items. "
                            "?item wdt:P625 ?coord. "
                            "{ ?item p:P131/ps:P131 ?local. ?local wdt:P31 wd:Q3184121. } "
                            "UNION "
                            "{ ?item p:P131/ps:P131 [wdt:P131 ?local]. ?local wdt:P31 wd:Q3184121. } "
                            "OPTIONAL {?item wdt:P18 ?P18} "
                            "OPTIONAL {?item wdt:P3311 ?P3311} "
                            "OPTIONAL {?item wdt:P4291 ?P4291} "
                            "OPTIONAL {?item wdt:P4640 ?P4640} "
                            "OPTIONAL {?item wdt:P8517 ?P8517} "
                            "OPTIONAL {?item wdt:P1442 ?P1442} "
                            "OPTIONAL {?item wdt:P1766 ?P1766} "
                            "OPTIONAL {?item wdt:P1801 ?P1801} "
                            "OPTIONAL {?item wdt:P3451 ?P3451} "
                            "OPTIONAL {?item wdt:P5252 ?P5252} "
                            "OPTIONAL {?item wdt:P5775 ?P5775} "
                            "OPTIONAL {?item wdt:P8592 ?P8592} "
                            "OPTIONAL {?item wdt:P9721 ?P9721} "
                            "OPTIONAL {?item wdt:P9906 ?P9906} "
                            "SERVICE wikibase:label { bd:serviceParam wikibase:language "
                            "'"+lang+",pt-br,pt,en,es,fr,de,ja,[AUTO_LANGUAGE]'.} "
                            "MINUS { ?item wdt:P31/wdt:P279* wd:Q22698. } "
                            "MINUS { ?item wdt:P31/wdt:P279* wd:Q473972. } "
                            "MINUS { ?item wdt:P31/wdt:P279* wd:Q271669. } "
                            "}")
    items = []
    if "bindings" in result["results"] and result["results"]["bindings"]:
        for item in result["results"]["bindings"]:
            qid = item["item"]["value"].replace("http://www.wikidata.org/entity/", "")
            coord = item["coord"]["value"].replace("Point(", "").replace(")", "").split()
            label = item["itemLabel"]["value"]
            p18 = unquote(item["P18"]["value"]).replace("http://commons.wikimedia.org/wiki/Special:FilePath/", "") if "P18" in item else ""
            p3311 = unquote(item["P3311"]["value"]).replace("http://commons.wikimedia.org/wiki/Special:FilePath/", "") if "P3311" in item else ""
            p4291 = unquote(item["P4291"]["value"]).replace("http://commons.wikimedia.org/wiki/Special:FilePath/", "") if "P4291" in item else ""
            p4640 = unquote(item["P4640"]["value"]).replace("http://commons.wikimedia.org/wiki/Special:FilePath/", "") if "P4640" in item else ""
            p8517 = unquote(item["P8517"]["value"]).replace("http://commons.wikimedia.org/wiki/Special:FilePath/", "") if "P8517" in item else ""
            p1442 = unquote(item["P1442"]["value"]).replace("http://commons.wikimedia.org/wiki/Special:FilePath/", "") if "P1442" in item else ""
            p1766 = unquote(item["P1766"]["value"]).replace("http://commons.wikimedia.org/wiki/Special:FilePath/", "") if "P1766" in item else ""
            p1801 = unquote(item["P1801"]["value"]).replace("http://commons.wikimedia.org/wiki/Special:FilePath/", "") if "P1801" in item else ""
            p3451 = unquote(item["P3451"]["value"]).replace("http://commons.wikimedia.org/wiki/Special:FilePath/", "") if "P3451" in item else ""
            p5252 = unquote(item["P5252"]["value"]).replace("http://commons.wikimedia.org/wiki/Special:FilePath/", "") if "P5252" in item else ""
            p5775 = unquote(item["P5775"]["value"]).replace("http://commons.wikimedia.org/wiki/Special:FilePath/", "") if "P5775" in item else ""
            p8592 = unquote(item["P8592"]["value"]).replace("http://commons.wikimedia.org/wiki/Special:FilePath/", "") if "P8592" in item else ""
            p9721 = unquote(item["P9721"]["value"]).replace("http://commons.wikimedia.org/wiki/Special:FilePath/", "") if "P9721" in item else ""
            p9906 = unquote(item["P9906"]["value"]).replace("http://commons.wikimedia.org/wiki/Special:FilePath/", "") if "P9906" in item else ""

            imagem = next(filter(lambda img: img, [p18, p3451, p5775, p8592, p9721, p4291, p8517, p5252, p1801,
                                                   p1766, p9906, p1442, p4640, p3311]), "No-image.png")

            items.append({
                "item": qid,
                "coord": coord,
                "imagem": imagem,
                "label": label,
                "p18": p18,
                "p3451": p3451,
                "p5775": p5775,
                "p8592": p8592,
                "p9721": p9721,
                "p4291": p4291,
                "p8517": p8517,
                "p5252": p5252,
                "p1801": p1801,
                "p1766": p1766,
                "p9906": p9906,
                "p1442": p1442,
                "p4640": p4640,
                "p3311": p3311})
    return items


def query_monuments_without_coords(qid, lang):
    result = query_wikidata("SELECT DISTINCT ?item ?itemLabel ?local ?localLabel ?imagem ?endereço "
                            "WITH { "
                            "SELECT DISTINCT ?item ?local WHERE { "
                            "?item wdt:P131* wd:" + qid + "; wdt:P1435 []. "
                            "} } AS %items "
                            "WITH { "
                            "SELECT DISTINCT ?item ?local "
                            "(SAMPLE(?imagem) AS ?imagem) (SAMPLE(?endereço) AS ?endereço) WHERE { "
                            "INCLUDE %items. "
                            "{ ?item p:P131/ps:P131 ?local. ?local wdt:P31 wd:Q3184121. } "
                            "UNION "
                            "{ ?item p:P131/ps:P131 [wdt:P131 ?local]. ?local wdt:P31 wd:Q3184121. } "
                            "OPTIONAL {?item wdt:P18|wdt:P18|wdt:P3311|wdt:P4291|wdt:P4640|wdt:P8517|wdt:P1442|"
                            "wdt:P1766|wdt:P1801|wdt:P3451|wdt:P5252|wdt:P5775|wdt:P8592|wdt:P9721|wdt:P9906 ?imagem } "
                            "OPTIONAL {?item wdt:P6375 ?endereço} } GROUP BY ?item ?local "
                            "} AS %filtered "
                            "WHERE { "
                            "INCLUDE %filtered. "
                            "MINUS { ?item wdt:P31/wdt:P279* wd:Q22698. } "
                            "MINUS { ?item wdt:P31/wdt:P279* wd:Q473972. } "
                            "MINUS { ?item wdt:P31/wdt:P279* wd:Q271669. } "
                            "MINUS { ?item wdt:P625 ?coord. } "
                            "SERVICE wikibase:label { bd:serviceParam wikibase:language "
                            "'"+lang+",pt-br,pt,en,es,fr,de,ja,[AUTO_LANGUAGE]'. } }")
    items = []
    locais = []
    if "bindings" in result["results"] and result["results"]["bindings"]:
        for item in result["results"]["bindings"]:
            qid = item["item"]["value"].replace("http://www.wikidata.org/entity/", "")
            label = item["itemLabel"]["value"]
            local_qid = item["local"]["value"].replace("http://www.wikidata.org/entity/", "")
            local_label = item["localLabel"]["value"]
            imagem = unquote(item["imagem"]["value"])+"?width=100px" if "imagem" in item else url_for("static", filename="images/No-image.png")
            endereco = item["endereço"]["value"] if "endereço" in item else ""
            items.append({
                "item": qid,
                "imagem": imagem,
                "label": label,
                "local": local_qid,
                "local_label": local_label,
                "endereço": endereco})
            locais.append(local_label)

    return items, list(set(locais))


def query_monument(qid, lang):
    result = query_wikidata("SELECT DISTINCT ?item ?itemLabel ?coord ?endereço ?localLabel ?estadoLabel ?paísLabel "
                            "?commons_cat ?tombamento_id ?tombamentoLabel ?número_de_inventário ?P18 ?P3311 ?P4291 "
                            "?P4640 ?P8517 ?P1442 ?P1766 ?P1801 ?P3451 ?P5252 ?P5775 ?P8592 ?P9721 ?P9906 "
                            "WITH { "
                            "SELECT DISTINCT ?item (SAMPLE(?coord) AS ?coord) ?endereço ?local ?estado "
                            "?país ?commons_cat ?tombamento_id ?tombamento ?número_de_inventário "
                            "?P18 ?P3311 ?P4291 ?P4640 ?P8517 ?P1442 ?P1766 ?P1801 "
                            "?P3451 ?P5252 ?P5775 ?P8592 ?P9721 ?P9906 "
                            "WHERE { "
                            "BIND(wd:"+qid+" AS ?item) "
                            "?item wdt:P625 ?coord. "
                            "OPTIONAL{?item wdt:P6375 ?endereço} "
                            "{ ?item p:P131/ps:P131 ?local. ?local wdt:P31 wd:Q3184121. } "
                            "UNION "
                            "{ ?item p:P131/ps:P131 [wdt:P131 ?local]. ?local wdt:P31 wd:Q3184121. } "
                            "?local wdt:P131 ?estado. ?estado wdt:P31 wd:Q485258. "
                            "?item wdt:P17 ?país. "
                            "OPTIONAL {?item wdt:P18 ?P18} "
                            "OPTIONAL {?item wdt:P3311 ?P3311} "
                            "OPTIONAL {?item wdt:P4291 ?P4291} "
                            "OPTIONAL {?item wdt:P4640 ?P4640} "
                            "OPTIONAL {?item wdt:P8517 ?P8517} "
                            "OPTIONAL {?item wdt:P1442 ?P1442} "
                            "OPTIONAL {?item wdt:P1766 ?P1766} "
                            "OPTIONAL {?item wdt:P1801 ?P1801} "
                            "OPTIONAL {?item wdt:P3451 ?P3451} "
                            "OPTIONAL {?item wdt:P5252 ?P5252} "
                            "OPTIONAL {?item wdt:P5775 ?P5775} "
                            "OPTIONAL {?item wdt:P8592 ?P8592} "
                            "OPTIONAL {?item wdt:P9721 ?P9721} "
                            "OPTIONAL {?item wdt:P9906 ?P9906} "
                            "OPTIONAL{?item wdt:P373 ?commons_cat} "
                            "OPTIONAL{?item p:P1435 ?tombamento_id. "
                            "?tombamento_id ps:P1435 ?tombamento. "
                            "OPTIONAL {?tombamento_id pq:P217 ?número_de_inventário}.} "
                            "} GROUP BY ?item ?itemLabel ?endereço ?local ?estado ?país ?commons_cat "
                            "?tombamento_id ?tombamento ?número_de_inventário ?P18 ?P3311 ?P4291 ?P4640"
                            "?P8517 ?P1442 ?P1766 ?P1801 ?P3451 ?P5252 ?P5775 ?P8592 ?P9721 ?P9906 } AS %item "
                            "WHERE { "
                            "INCLUDE %item. "
                            "SERVICE wikibase:label { bd:serviceParam wikibase:language '"+lang+",pt-br,pt,en,[AUTO_LANGUAGE]'. }}")

    qid_set = []    #
    coord_set = []    #
    label_set = []    #
    address_set = []    #
    commons_cat_set = []    #
    local_set = []    #
    estado_set = []    #
    pais_set = []    #
    tombamentos = {}
    p18 = ""
    p3311 = ""
    p4291 = ""
    p4640 = ""
    p8517 = ""
    p1442 = ""
    p1766 = ""
    p1801 = ""
    p3451 = ""
    p5252 = ""
    p5775 = ""
    p8592 = ""
    p9721 = ""
    p9906 = ""

    if "bindings" in result["results"] and result["results"]["bindings"]:
        for item in result["results"]["bindings"]:
            qid_set.append(item["item"]["value"].replace("http://www.wikidata.org/entity/", "")) if "item" in item else qid_set.append("")
            coord_set = item["coord"]["value"].replace("Point(", "").replace(")", "").split() if "coord" in item else ""
            label_set.append(item["itemLabel"]["value"]) if "itemLabel" in item else label_set.append("")
            address_set.append(item["endereço"]["value"]) if "endereço" in item else address_set.append("")
            commons_cat_set.append(item["commons_cat"]["value"]) if "commons_cat" in item else commons_cat_set.append("")
            local_set.append(item["localLabel"]["value"]) if "localLabel" in item else local_set.append("")
            estado_set.append(item["estadoLabel"]["value"]) if "estadoLabel" in item else estado_set.append("")
            pais_set.append(item["paísLabel"]["value"]) if "paísLabel" in item else pais_set.append("")

            p18 = unquote(item["P18"]["value"]) if "P18" in item else ""
            p3311 = unquote(item["P3311"]["value"]) if "P3311" in item else ""
            p4291 = unquote(item["P4291"]["value"]) if "P4291" in item else ""
            p4640 = unquote(item["P4640"]["value"]) if "P4640" in item else ""
            p8517 = unquote(item["P8517"]["value"]) if "P8517" in item else ""
            p1442 = unquote(item["P1442"]["value"]) if "P1442" in item else ""
            p1766 = unquote(item["P1766"]["value"]) if "P1766" in item else ""
            p1801 = unquote(item["P1801"]["value"]) if "P1801" in item else ""
            p3451 = unquote(item["P3451"]["value"]) if "P3451" in item else ""
            p5252 = unquote(item["P5252"]["value"]) if "P5252" in item else ""
            p5775 = unquote(item["P5775"]["value"]) if "P5775" in item else ""
            p8592 = unquote(item["P8592"]["value"]) if "P8592" in item else ""
            p9721 = unquote(item["P9721"]["value"]) if "P9721" in item else ""
            p9906 = unquote(item["P9906"]["value"]) if "P9906" in item else ""

            if "tombamento_id" in item:
                tombamentos[item["tombamento_id"]["value"].replace("http://www.wikidata.org/entity/statement/", "").replace("-", "$", 1)] = {
                    "label": item["tombamentoLabel"]["value"] if "tombamentoLabel" in item else "",
                    "num": item["número_de_inventário"]["value"] if "número_de_inventário" in item else "",
                }

    image = next(filter(lambda img: img, [p18, p3451, p5775, p8592, p9721, p4291, p8517, p5252, p1801, p1766, p9906, p1442, p4640, p3311]), os.path.join(url_for("static", filename="images/No-image.png")))
    qid_set = list(set(qid_set))
    label_set = list(set(label_set))
    address_set = list(set(address_set))
    commons_cat_set = list(set(commons_cat_set))
    local_set = list(set(local_set))
    estado_set = list(set(estado_set))
    pais_set = list(set(pais_set))

    object_ = {
        "qid": qid_set,
        "image": image,
        "label": label_set,
        "coord": coord_set,
        "address": address_set,
        "commons_cat": commons_cat_set,
        "local": local_set,
        "state": estado_set,
        "country": pais_set,
        "designated_patrimony": tombamentos,
        "p18": p18,
        "p3311": p3311,
        "p4291": p4291,
        "p4640": p4640,
        "p8517": p8517,
        "p1442": p1442,
        "p1766": p1766,
        "p1801": p1801,
        "p3451": p3451,
        "p5252": p5252,
        "p5775": p5775,
        "p8592": p8592,
        "p9721": p9721,
        "p9906": p9906,
    }

    return object_


def get_item(qid, lang):
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbgetentities",
        "ids": qid,
        "languages": lang,
        "languagefallback": "pt",
        "format": "json"
    }

    result = requests.get(url=url, params=params, headers={'User-agent': 'WLM Brasil'})

    data = result.json()
    properties = data["entities"][qid]["claims"]


def get_category_info(cat):
    url = "https://commons.wikimedia.org/w/api.php"
    cat = "Category:" + cat if not cat.startswith("Category:") else cat
    params = {
        "action": "query",
        "prop": "categoryinfo",
        "format": "json",
        "titles": cat
    }

    result = requests.get(url=url, params=params, headers={'User-agent': 'WLM Brasil'})

    data = result.json()
    for key, val in data["query"]["pages"].items():
        if "categoryinfo" in val:
            return {"subcats": val["categoryinfo"]["subcats"], "files": val["categoryinfo"]["files"]}
        else:
            return False


def get_article(lang, article):
    if lang == "pt-br":
        lang = "pt"
    url = "https://"+lang+".wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "extracts",
        "titles": article,
        "redirects": "true",
        "exintro": 1,
        "format": "json"
    }

    result = requests.get(url=url, params=params, headers={'User-agent': 'WLM Brasil'})
    data = result.json()
    return data["query"]["pages"].values().__iter__().__next__()["extract"]


def get_sitelinks(qid):
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbgetentities",
        "props": "sitelinks",
        "ids": qid,
        "format": "json"
    }

    result = requests.get(url=url, params=params, headers={'User-agent': 'WLM Brasil'})
    data = result.json()

    sitelinks = {}
    sitelinks_json = data["entities"][qid]["sitelinks"]
    for key, val in sitelinks_json.items():
        if key != "commonswiki":
            sitelinks[key.split('wiki')[0]] = val["title"]

    return sitelinks


def api_post_request(params):
    app = current_app
    url = 'https://www.wikidata.org/w/api.php'
    client_key = app.config['CONSUMER_KEY']
    client_secret = app.config['CONSUMER_SECRET']
    oauth = OAuth1Session(client_key,
                          client_secret=client_secret,
                          resource_owner_key=session['owner_key'],
                          resource_owner_secret=session['owner_secret'])
    return oauth.post(url, data=params, timeout=4)