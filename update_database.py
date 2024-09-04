import pandas as pd
import aiohttp
import asyncio
import nest_asyncio
from wikidata import get_monuments
from models import Monument, monument_state
from db import db

nest_asyncio.apply()


def chunk_data(data, chunk_size):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def extract_claim(claims, prop, type_=None, image_=None):
    if image_ is None:
        image_ = []
    if type_ is None:
        type_ = []
    img = ""
    if prop in claims:
        type_.append(f".addTo({prop})")
        img = claims[prop][0].get('mainsnak', {}).get('datavalue', {}).get('value')

    image_.append(img)
    return img


def extract_coord(claims, prop):
    lat = 90
    lon = 180
    if prop in claims:
        coord_value = claims[prop][0].get('mainsnak', {}).get('datavalue', {}).get('value', {})
        lat = coord_value.get("latitude", 90)
        lon = coord_value.get("longitude", 180)
    return [lat, lon]


async def get_entities(session, qids):
    base_url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbgetentities",
        "format": "json",
        "props": "labels|descriptions|claims",
        "ids": "|".join(qids)
    }

    async with session.get(base_url, params=params) as response:
        data = await response.json()

    results = []

    if "entities" in data:
        for qid, entity in data["entities"].items():
            labels = entity.get("labels", {})
            descr = entity.get("descriptions", {})
            claims = entity.get("claims", {})
            coords = extract_coord(claims, "P625")
            type_ = []
            image_ = []

            result = {
                'item': qid,
                'coord_lat': coords[1],
                'coord_lon': coords[0],
                'label': labels.get('pt-br', {}).get('value', labels.get('pt', {}).get('value', '')),
                'label_en': labels.get('en', {}).get('value', ''),
                'descr': descr.get('pt-br', {}).get('value', descr.get('pt', {}).get('value', '')),
                'descr_en': descr.get('en', {}).get('value', ''),
                'p18': extract_claim(claims, 'P18', type_, image_),
                'p5775': extract_claim(claims, 'P5775', type_, image_),
                'p9721': extract_claim(claims, 'P9721', type_, image_),
                'p9906': extract_claim(claims, 'P9906', type_, image_),
                'p1801': extract_claim(claims, 'P1801', type_, image_),
                'p1766': extract_claim(claims, 'P1766', type_, image_),
                'p8592': extract_claim(claims, 'P8592', type_, image_),
                'p3451': extract_claim(claims, 'P3451', type_, image_),
                'p4291': extract_claim(claims, 'P4291', type_, image_),
                'p8517': extract_claim(claims, 'P8517', type_, image_),
                'p3311': extract_claim(claims, 'P3311', type_, image_),
                "types": str(type_),
                "imagem": next((img for img in image_ if img), "")
            }

            results.append(result)
    return results


async def get_batch_entities(qids):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for chunk in chunk_data(qids, 50):
            tasks.append(get_entities(session, chunk))
        results = await asyncio.gather(*tasks)
    return [item for sublist in results for item in sublist]


def get_entities_from_wikidata():
    monuments_and_locals_df = get_monuments()
    qids = monuments_and_locals_df["item"].drop_duplicates().tolist()
    monuments = asyncio.run(get_batch_entities(qids))

    return monuments, monuments_and_locals_df


def prepare_monuments(monuments):
    df = pd.DataFrame(monuments)
    ids = df["item"].tolist()

    existing_entries = Monument.query.filter(Monument.item.in_(ids)).all()
    existing_entries_dict = {entry.item: entry for entry in existing_entries}

    to_update = []
    to_create = []

    for entry in monuments:
        if entry['item'] in existing_entries_dict:
            existing_entry = existing_entries_dict[entry['item']]
            existing_entry.item = entry["item"]
            existing_entry.coord_lat = entry["coord_lat"]
            existing_entry.coord_lon = entry["coord_lon"]
            existing_entry.label = entry["label"]
            existing_entry.label_en = entry["label_en"]
            existing_entry.descr = entry["descr"]
            existing_entry.descr_en = entry["descr_en"]
            existing_entry.imagem = entry["imagem"]
            existing_entry.types = entry["types"]
            existing_entry.p18 = entry["p18"]
            existing_entry.p3451 = entry["p3451"]
            existing_entry.p5775 = entry["p5775"]
            existing_entry.p8592 = entry["p8592"]
            existing_entry.p9721 = entry["p9721"]
            existing_entry.p4291 = entry["p4291"]
            existing_entry.p8517 = entry["p8517"]
            existing_entry.p1801 = entry["p1801"]
            existing_entry.p1766 = entry["p1766"]
            existing_entry.p9906 = entry["p9906"]
            existing_entry.p3311 = entry["p3311"]
            to_update.append(existing_entry)
        else:
            new_entry = Monument(**entry)
            to_create.append(new_entry)

    return to_update, to_create


def insert_associations_into_database(df):
    df.rename(columns={'item': 'monument_id', 'local': 'state_id'}, inplace=True)
    associations = df.to_dict(orient='records')
    select = monument_state.select()
    existing_associations = db.session.execute(select).fetchall()

    existing_set = set((row[0], row[1]) for row in existing_associations)

    new_associations = [association for association in associations if
                        (association['monument_id'], association['state_id']) not in existing_set]

    if new_associations:
        db.session.execute(monument_state.insert(), new_associations)
        db.session.commit()


def insert_entries_into_database(monuments, monuments_and_locals_df):
    to_update, to_create = prepare_monuments(monuments)
    if to_update:
        db.session.bulk_save_objects(to_update)
    if to_create:
        db.session.bulk_save_objects(to_create)
    db.session.commit()

    insert_associations_into_database(monuments_and_locals_df)
