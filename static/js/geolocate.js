const osm_map = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 17,
    minZoom: 1,
    attribution: '&copy; <a href="https://openstreetmap.org/copyright">' + credits + '</a>'
});

const blueIcon = L.AwesomeMarkers.icon({
    icon: 'fa-solid fa-landmark',
    markerColor: 'darkblue',
    iconColor: 'white',
    prefix: 'fas'
});

let map = L.map('map', {layers: [osm_map]}).setMaxBounds(bounds);

let marker = L.marker({lat: -90, lon: 0}, {icon: blueIcon, draggable: true});

let toggleMarker = false;

// Functions

// This code adds the variable information for each monument
// based on the row of the table of the button clicked.
$("td button").click(function () {
    $('#addModal').modal('show');
    $('#addCoordinates').data('item', this.dataset['item']);
    $('#monument').html(this.dataset['label']);
    $('#local').html(this.dataset['local'] + '<br>');
    $('#address').html(this.dataset['address'] + '<br>');
});

// This code makes sure the map loads ok inside the modal window
$('#addModal').on('shown.bs.modal', function () {
    map.invalidateSize();
    map.fitBounds(bounds);
});

$('#addModal').on('hidden.bs.modal', function () {
    marker.setLatLng({lat: -90, lon: 0});
    map.removeLayer(marker);
    localizar.state('locate');
    localizar.button.style.backgroundColor = "#007bff";
    $('#addCoordinates').prop('disabled', true);
    $('#latlng').val("").prop("disabled", false);
    $('#latlngConfirm').prop("disabled", false);
});

$(document).ready(function(){
    $("#localFilter").on("keyup", function() {
        var value = $(this).val().toLowerCase();
        $("#monuments_table tr").filter(function() {
            $(this).toggle($(this).find("td:nth-child(2) a:nth-child(3)").text().toLowerCase().indexOf(value) > -1);
        });
    });
});

// Post coordinates on item on Wikidata
function postCoordinates() {
    var object = $('#addCoordinates')
    var item = object.data('item');
    var lat = object.data('lat');
    var lon = object.data('lon');
    var data = {'item': item, 'lat': lat, 'lon': lon};
    var erro = '{{ _("Erro") }}';

    $.ajax({
        url: "/postCoordinates",
        type: "POST",
        data: JSON.stringify(data),
        contentType: "application/json",
        dataType: "json",

        success: function (response) {
            $("#"+response.qid+"_row").css("background-color","#B2FF54");
            alert(response.message);
        },
        error: function (response) {
            alert(erro);
        }
    });
}

$("#latlngConfirm").on('click', function () {
    $(this).toggleClass("cancel");
    $(this).find("i").toggleClass("fa fa-solid fa-xmark");
    let nCoordinate = 0;
    let wCoordinate = 0;
    toggleMarker = !toggleMarker;

    if(toggleMarker) {
        let coords = $("#latlng").val().replace(/\s+/g, '');
        const gsmCoordinatesRegex = new RegExp("(\\d+)(º|°)(\\d+)'(.*)\"(N|S)(\\d+)(º|°)(\\d+)'(.*)\"(W|E|L|O)");
        const decimalCoordinatesRegex = new RegExp("(.*),(.*)");
        if (gsmCoordinatesRegex.test(coords)) {
            let match = gsmCoordinatesRegex.exec(coords);
            let directionNS = -1;
            let directionWE = -1;

            if (match[5] === "N") {
                directionNS = 1
            }
            if (match[10] === "E" || match[10] === "L") {
                directionWE = 1
            }

            nCoordinate = directionNS * (parseFloat(match[1]) + parseFloat(match[3]) / 60 + parseFloat(match[4]) / 3600);
            wCoordinate = directionWE * (parseFloat(match[6]) + parseFloat(match[8]) / 60 + parseFloat(match[9]) / 3600);
        } else if (decimalCoordinatesRegex.test(coords)) {
            let match = decimalCoordinatesRegex.exec(coords);
            nCoordinate = match[1];
            wCoordinate = match[2];
        }
        var newLatLng = new L.LatLng(nCoordinate, wCoordinate);
        marker.setLatLng(newLatLng).addTo(map);
        var object = $('#addCoordinates');
        object.data('lat', nCoordinate);
        object.data('lon', wCoordinate);
        object[0].toggleAttribute('disabled');
        $(".easy-button-button.leaflet-bar-part.leaflet-interactive").prop("disabled", true);
    } else {
        let newLatLng = new L.LatLng(nCoordinate, wCoordinate);
        marker.setLatLng(newLatLng);
        map.removeLayer(marker);
        $(".easy-button-button.leaflet-bar-part.leaflet-interactive").prop("disabled", false);
    }
})

// Buttons
// This code adds a button for users locate themselves in the map
const locate = L.control.locate({
    flyTo: true,
    returnToPrevBounds: true,
    icon: 'locate fa-solid fa-location-dot',
    iconElementTag: 'i',
    strings: {
        title: whereAmIMsg
    },
}).addTo(map);

// This code adds a button for users add a marker for the monument
// in the map
var localizar = L.easyButton({
    states: [
        {
            stateName: 'locate',
            icon: 'fa-solid fa-map-pin',
            title: localizeMsg,
            onClick: function (btn, map) {
                map.addLayer(marker);
                btn.state('cancel');
                btn.button.style.backgroundColor = '#990000';
                $("#latlng").prop("disabled",true);
                $("#latlngConfirm").prop("disabled",true);
                map.on('mousemove', function (e) {
                    marker.setLatLng(e.latlng);
                    $("#latlng").val(e.latlng.lat+", "+e.latlng.lng);
                }); // Makes the marker follow the mouse
                map.on('click', function (e) {
                    marker.setLatLng(e.latlng);
                    map.off('mousemove');
                    var object = $('#addCoordinates');
                    object.data('lat', e.latlng.lat);
                    object.data('lon', e.latlng.lng);
                    object.prop('disabled', false);

                    $("#latlng").val(e.latlng.lat+", "+e.latlng.lng);
                    $("#latlngConfirm").val(e.latlng.lat+", "+e.latlng.lng);
                }); // Fixes the marker
            }
        },
        {
            stateName: 'cancel',
            icon: 'fa-solid fa-xmark',
            title: cancelMsg,
            onClick: function (btn, map) {
                marker.setLatLng([-90, 0]);
                map.removeLayer(marker);
                btn.state('locate');
                btn.button.style.backgroundColor = '#007bff';
                map.off('click'); // Deactivate the click function
                $('#addCoordinates').prop('disabled', true);

                $("#latlng").prop("disabled",false);
                $("#latlngConfirm").prop("disabled",false);
            }
        }]
}).addTo(map);

// This code adds a button for users to full screen the map
let fullScreen = new L.Control.Fullscreen({
    title: {
        'false': fullScreenFalse,
        'true': fullScreenTrue
    }
}).addTo(map);

// Actions
localizar.button.style.backgroundColor = "#007bff";
localizar.button.style.color = "#FFFFFF";