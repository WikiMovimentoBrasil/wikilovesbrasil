////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// CONSTANTS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
const colorTriples = [
    ["#006400", "#004B23", "#FFFFFF"],
    ["#D90202", "#7C0606", "#FFFFFF"],
    ["#FFA200", "#FF5900", "#000000"],
    ["#005A8A", "#03045E", "#FFFFFF"],
    ["#6818A5", "#3A015C", "#FFFFFF"],
    ["#FFFFFF", "#000000", "#000000"]
]

const regions = ["N", "NE", "CO", "SE", "S"]

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// MAP LAYER
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
let map = L.map('map', {zoomControl: false}).setMaxBounds([[6.3, -75.1], [-34.8, -27.8]]).setView([-19.5, -54.4], 4);

// OpenStreetMap
let osm_map = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    minZoom: 4,
    attribution: credits_osm
}).addTo(map);

// Wikimedia
const wm_map = L.tileLayer('https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png', {
    maxZoom: 19,
    minZoom: 4,
    attribution: credits_wikimedia
});

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// BUTTONS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Title
L.Control.Textbox = L.Control.extend({
		onAdd: function(map) {
		let text = L.DomUtil.create('div', 'map-instructions');
		text.id = "info_text";
		text.innerHTML = "<strong style='font-size: 150%'>" + instruction + "</strong>"
		return text;
		},

		onRemove: function(map) {}
	});
L.control.textbox = function(opts) { return new L.Control.Textbox(opts);}
L.control.textbox({ position: 'topleft' }).addTo(map);

// Zoom
L.control.zoom({
    position: 'bottomright'
}).addTo(map);

// Locate
let locate = L.control.locate({
    flyTo: true,
    position: 'bottomright',
    returnToPrevBounds: true,
    icon: 'locate fa-solid fa-location-dot',
    iconElementTag: 'i',
    strings: {
        title: whereAmIMsg
    },
}).addTo(map);

// Layers
L.control.layers({"OpenStreetMap": osm_map, "Wikimedia": wm_map}, null, {position: 'bottomright'}).addTo(map);

// Logo
L.Control.Watermark = L.Control.extend({
    onAdd: function (map) {
        var img = L.DomUtil.create('img');
        img.src = logo_path;
        img.style.width = '108px';
        img.style.marginBottom = '26px';
        return img;
    }
});
L.control.watermark = function (opts) {
    return new L.Control.Watermark(opts);
}
L.control.watermark({position: 'bottomleft'}).addTo(map);

// Menu
L.easyButton({
    states: [{
        icon: "<i class='fa-solid fa-bars'></i> ",
        stateName: 'menu',
        onClick: function () {
            $('#presentationModal').modal('show');
        }
    }]
}).addTo(map);

// Language
L.easyButton(
    "<i class='fa-solid fa-language'></i>",
    function () { $('#langModal').modal('show'); },
    langTooltip
).addTo(map);

// Info
L.easyButton(
    '<i class="fa-solid fa-info"></i>',
    function () { $('#aboutModal').modal('show'); },
    infoTooltip
).addTo(map);

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// FUNCTIONS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
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

    // info.update(layer.feature.properties);
}

// This code resets the original style once the mouse is not over
// the state
function resetHighlight(e) {
    states.resetStyle(e.target);
    // info.update();
}

// This code makes the map zoom and center the state selected
function zoomToFeature(e) {
    map.fitBounds(e.target.getBounds());
}

function openFeature(e) {
    window.open("/mapa/"+e.target.feature.properties.uf.toLowerCase(), "_self");
}

// When the user click in any state on the map, executes
// the appropriate functions
function selectFunction(e) {
    zoomToFeature(e);
    openFeature(e);
}

// When the user passes the mouse over a state on the map,
// executes the appropriate functions
function onEachFeature(feature, layer) {
    layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        click: selectFunction
    });
}

let states = L.geoJson(statesData, {style: style, onEachFeature: onEachFeature}).addTo(map);