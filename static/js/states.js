const colorTriples = [
    ["#006400", "#004B23", "#FFFFFF"],
    ["#D90202", "#7C0606", "#FFFFFF"],
    ["#FFA200", "#FF5900", "#000000"],
    ["#005A8A", "#03045E", "#FFFFFF"],
    ["#6818A5", "#3A015C", "#FFFFFF"],
    ["#FFFFFF", "#000000", "#000000"]
]

const regions = ["N", "NE", "CO", "SE", "S"]

var map = L.map('map', {zoomControl:false}).setMaxBounds([[6.3, -75.1], [-34.8, -27.8]]).setView([-19.5, -54.4], 4);

const osm_map = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 7,
    minZoom: 4,
    attribution: credits_osm
}).addTo(map);

const wm_map = L.tileLayer('https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png', {
    maxZoom: 7,
    minZoom: 4,
    attribution: credits_wikimedia
});

// Zoom
L.control.zoom({
    position: 'bottomright'
}).addTo(map);

// Locate
var locate = L.control.locate({
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
L.control.layers({"OpenStreetMap": osm_map, "Wikimedia": wm_map}, null,{position: 'bottomright'}).addTo(map);

// Logo at bottom left
L.Control.Watermark = L.Control.extend({
    onAdd: function(map) {
        var img = L.DomUtil.create('img');
        img.src = logoImage;
        img.style.width = '108px';
        img.style.marginBottom = '26px';
        return img;
    }
});
L.control.watermark = function(opts) { return new L.Control.Watermark(opts); }
L.control.watermark({ position: 'bottomleft' }).addTo(map);

// Menu
const menuButton = L.easyButton({
    states:[{
        icon: "<i class='fa-solid fa-bars'></i> " + menuName,
        stateName: 'menu',
        onClick: function(){ $('#presentationModal').modal('show'); }}]}).addTo(map);

// Functions

//This code opens the homepage sidemodal at loading
$(window).on('load', function() {
    $('#presentationModal').modal('show');
});

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
    estados.resetStyle(e.target);
    // info.update();
}

// This code makes the map zoom and center the state selected
function zoomToFeature(e) {
    map.fitBounds(e.target.getBounds());
}

function openFeature(e) {
    window.open("/mapa/"+e.target.feature.properties.uf.toLowerCase(), "_self");
}

// This code fills the modal instance with information and buttons
// about the state selected
// function showFeature(e) {
//     const nameObject = $("#nome");
//     nameObject.text(youSelectedMsg + "\n" + e.target.feature.properties.name);
//     nameObject.html(nameObject.html().replace(/\n/g, '<br/>'));
//     const uf = e.target.feature.properties.uf.toLowerCase();
//     $("#uf_monuments").attr("href", "/mapa/" + uf);
//     $("#uf_monuments_without_coordinates").attr("href", "/mapa/" + uf + "/geolocalizar");
//     $("#uf_monuments_suggestion").attr("href", "/mapa/sugerir?uf=" + uf);
//     $("#uf_monuments button").css({
//         "background-color": getBorderColor(e.target.feature.properties.region),
//         "color": getFontColor(e.target.feature.properties.region)
//     });
//     $("#uf_monuments_without_coordinates button").css({
//         "background-color": getFillColor(e.target.feature.properties.region),
//         "color": getFontColor(e.target.feature.properties.region)
//     });
// }

// This code opens the modal with a delay
// function openModal() {
//     window.setTimeout(function () {
//         $('#selectionModal').modal('show');
//     }, 750)
// }

// When the user click in any state on the map, executes
// the appropriate functions
function selectFunction(e) {
    zoomToFeature(e);
    openFeature(e);
    // showFeature(e);
    // openModal();
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