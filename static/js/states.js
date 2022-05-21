const colorTriples = [
    ["#006400", "#004B23", "#FFFFFF"],
    ["#D90202", "#7C0606", "#FFFFFF"],
    ["#FFA200", "#FF5900", "#000000"],
    ["#005A8A", "#03045E", "#FFFFFF"],
    ["#6818A5", "#3A015C", "#FFFFFF"],
    ["#FFFFFF", "#000000", "#000000"]
]

const regions = ["N", "NE", "CO", "SE", "S"]

const osm_map = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 7,
    minZoom: 4,
    attribution: '&copy; <a href="https://openstreetmap.org/copyright">' + credits + '</a>'
});

var map = L.map('map', {layers: [osm_map]}).setMaxBounds([[6.3, -75.1], [-34.8, -27.8]]).setView([-19.5, -54.4], 4);

// Functions

// This code defines the fill color of each state based on its region
function getFillColor(d) {
    return d === regions[0] ? colorTriples[0][0] :
        d === regions[1] ? colorTriples[1][0] :
            d === regions[2] ? colorTriples[2][0] :
                d === regions[3] ? colorTriples[3][0] :
                    d === regions[4] ? colorTriples[4][0] :
                        colorTriples[5][0];
}

// This code defines the bordr color of each state based on its region
function getBorderColor(d) {
    return d === regions[0] ? colorTriples[0][1] :
        d === regions[1] ? colorTriples[1][1] :
            d === regions[2] ? colorTriples[2][1] :
                d === regions[3] ? colorTriples[3][1] :
                    d === regions[4] ? colorTriples[4][1] :
                        colorTriples[5][1];
}

// This code defines the font color of each state based on its region
function getFontColor(d) {
    return d === regions[0] ? colorTriples[0][2] :
        d === regions[1] ? colorTriples[1][2] :
            d === regions[2] ? colorTriples[2][2] :
                d === regions[3] ? colorTriples[3][2] :
                    d === regions[4] ? colorTriples[4][2] :
                        colorTriples[5][2];
}

// This code defines the style of each state on load
function style(feature) {
    return {
        fillColor: getFillColor(feature.properties.region),
        weight: 1,
        opacity: 1,
        color: getBorderColor(feature.properties.region),
        fillOpacity: 0.7
    };
}

// This code createas a black border around the state border when
// the mouse is over it
function highlightFeature(e) {
    var layer = e.target;

    layer.setStyle({
        weight: 5,
        color: '#000000',
        dashArray: '',
        fillOpacity: 0.7
    });

    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
        layer.bringToFront();
    }
}

// This code resets the original style once the mouse is not over
// the state
function resetHighlight(e) {
    estados.resetStyle(e.target);
}

// This code makes the map zoom and center the state selected
function zoomToFeature(e) {
    map.fitBounds(e.target.getBounds());
}

// This code fills the modal instance with information and buttons
// about the state selected
function showFeature(e) {
    const nameObject = $("#nome");
    nameObject.text(youSelectedMsg + "\n" + e.target.feature.properties.name);
    nameObject.html(nameObject.html().replace(/\n/g, '<br/>'));
    const uf = e.target.feature.properties.uf.toLowerCase();
    $("#uf_monuments").attr("href", "/mapa/" + uf);
    $("#uf_monuments_without_coordinates").attr("href", "/mapa/" + uf + "/geolocalizar");
    $("#uf_monuments_suggestion").attr("href", "/mapa/sugerir?uf=" + uf);
    $("#uf_monuments button").css({
        "background-color": getBorderColor(e.target.feature.properties.region),
        "color": getFontColor(e.target.feature.properties.region)
    });
    $("#uf_monuments_without_coordinates button").css({
        "background-color": getFillColor(e.target.feature.properties.region),
        "color": getFontColor(e.target.feature.properties.region)
    });
}

// This code opens the modal with a delay
function openModal() {
    window.setTimeout(function () {
        $('#selectionModal').modal('show');
    }, 750)
}

// When the user click in any state on the map, executes
// the appropriate functions
function selectFunction(e) {
    zoomToFeature(e);
    showFeature(e);
    openModal();
}

// When the user passes the mouve over a state on the map,
// executes the appropriate functions
function onEachFeature(feature, layer) {
    layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        click: selectFunction
    });
}

const estados = L.geoJson(statesData, {style: style, onEachFeature: onEachFeature}).addTo(map);