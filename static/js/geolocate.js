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

var map = L.map('map', {layers: [osm_map]}).setMaxBounds(bounds);

var marker = L.marker({lat: -90, lon: 0}, {icon: blueIcon, draggable: true});

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
            alert(response);
        },
        error: function () {
            alert(erro);
        }
    });
}

$("#latlngConfirm").on('click', function () {
    let coords = $("#latlng").val();
    const gsmCoordinatesRegex = new RegExp("(\\d+)(º|°)(\\d+)'(.*)\"(N|S) (\\d+)(º|°)(\\d+)'(.*)\"(W|E|L|O)");
    const decimalCoordinatesRegex = new RegExp("(.*)(,|, | )(.*)");
    let nCoordinate = 0;
    let wCoordinate = 0;
    if (gsmCoordinatesRegex.test(coords)) {
        let match = gsmCoordinatesRegex.exec(coords);
        let directionNS = -1;
        let directionWE = -1;

        if (match[5] === "N") { directionNS = 1}
        if (match[10] === "E" || match[10] === "L") { directionWE = 1}

        nCoordinate = directionNS * (parseFloat(match[1]) + parseFloat(match[3])/60 + parseFloat(match[4])/3600);
        wCoordinate = directionWE * (parseFloat(match[6]) + parseFloat(match[8])/60 + parseFloat(match[9])/3600);
    }
    else if(decimalCoordinatesRegex.test(coords)) {
        let match = decimalCoordinatesRegex.exec(coords);
        nCoordinate = match[1];
        wCoordinate = match[3];
    }
    var newLatLng = new L.LatLng(nCoordinate, wCoordinate);
    marker.setLatLng(newLatLng).addTo(map);
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
                map.on('mousemove', function (e) {
                    marker.setLatLng(e.latlng);
                }); // Makes the marker follow the mouse
                map.on('click', function (e) {
                    marker.setLatLng(e.latlng);
                    map.off('mousemove');
                    var object = $('#addCoordinates')
                    object.data('lat', e.latlng.lat);
                    object.data('lon', e.latlng.lng);
                    object.prop('disabled', false);
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
            }
        }]
}).addTo(map);

// Actions
localizar.button.style.backgroundColor = "#007bff";
localizar.button.style.color = "#FFFFFF";