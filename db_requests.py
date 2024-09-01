from flask import url_for
from flask_babel import gettext
from models import Monument, monument_state


def get_pins(uf_qid):
    monuments = query_db_monuments(uf_qid)
    qids_with_image = []
    qids_without_image = []
    pins = []
    tooltip_style = "{direction:'top', offset: [0, -37]}"
    popup_style = "{closeButton: false}"
    button_message = gettext('Ver mais informações e enviar fotografias')

    for item in monuments:
        tooltip = item["label"].replace('"', '\\"')
        if tooltip != item["label"]:
            pass
        popup = (f"<span style='text-align:center'><b>{tooltip}</b></span><br><br>"
                 f"<a class='custom-link' target='_self' href='{url_for('monumento', qid=item['item'])}'>"
                 f"<button class='send_button'><i class='fa-solid fa-arrow-up-from-bracket'></i> "
                 f"{button_message}</div>")

        coord_str = f"{{lon: {item['coord'][0]}, lat: {item['coord'][1]}}}"
        icon_type = "greenIcon" if "imagem" in item and item["imagem"] != "No-image.png" else "redIcon"

        pin = (
            f"{item['item']} = L.marker({coord_str}, {{icon: {icon_type}, item: \"{item['item']}\", label: \"{tooltip}\"}})"
            f".bindTooltip(\"{tooltip}\", {tooltip_style}).bindPopup(\"{popup}\", {popup_style}).on('click', markerOnClick)"
        )

        if item["imagem"] != "No-image.png":
            types = item["types"]
            if types:
                pin += "".join(types)
            qids_with_image.append(item["item"])
        else:
            pin += ".addTo(markers_without_image)"
            qids_without_image.append(item["item"])

        pins.append(pin)

    return pins, qids_with_image, qids_without_image


def query_db_monuments(uf):
    result = (Monument.query.join(monument_state)
              .filter(monument_state.c.state_id == uf)
              .filter(Monument.coord_lat < 90)
              .all())
    result_dict = [monument.to_dict() for monument in result]
    return result_dict
