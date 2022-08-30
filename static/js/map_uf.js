////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// MAP LAYER
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
let map = L.map('map', {zoomControl: false}).setMaxBounds([[10, -20], [-40, -90]]);

// OpenStreetMap
let osm_map = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 17,
    minZoom: 4,
    attribution: credits_osm
}).addTo(map);

// Wikimedia
const wm_map = L.tileLayer('https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png', {
    maxZoom: 7,
    minZoom: 4,
    attribution: credits_wikimedia
});

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// ICONS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
let greenIcon = L.AwesomeMarkers.icon({
    icon: 'fa-solid fa-image',
    markerColor: 'green',
    iconColor: 'white',
    prefix: 'fas'
});

let greenblueIcon = L.AwesomeMarkers.icon({
    icon: 'fa-solid fa-image',
    markerColor: 'darkblue',
    iconColor: 'white',
    prefix: 'fas'
});

let redIcon = L.AwesomeMarkers.icon({
    icon: 'fa-camera',
    markerColor: 'red',
    iconColor: 'white',
    prefix: 'fa'
});

let redblueIcon = L.AwesomeMarkers.icon({
    icon: 'fa-camera',
    markerColor: 'darkblue',
    iconColor: 'white',
    prefix: 'fa'
});

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// CLUSTERS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
let markers_with_image = L.markerClusterGroup({
    maxClusterRadius: 100,
    disableClusteringAtZoom: 15,
    showCoverageOnHover: false,
    iconCreateFunction: function (cluster) {
        var markers = cluster.getAllChildMarkers();
        if (markers.length < 10) {
            return L.divIcon({
                html: '<div class="green-cluster green-circle-tiny">' + markers.length + '</div>',
                iconSize: L.point(20, 20)
            });
        } else if (markers.length < 25) {
            return L.divIcon({
                html: '<div class="green-cluster green-circle-small">' + markers.length + '</div>',
                iconSize: L.point(25, 25)
            });
        } else if (markers.length < 50) {
            return L.divIcon({
                html: '<div class="green-cluster green-circle-normal">' + markers.length + '</div>',
                iconSize: L.point(30, 30)
            });
        } else if (markers.length < 250) {
            return L.divIcon({
                html: '<div class="green-cluster green-circle-big">' + markers.length + '</div>',
                iconSize: L.point(35, 35)
            });
        } else {
            return L.divIcon({
                html: '<div class="green-cluster green-circle-large">' + markers.length + '</div>',
                iconSize: L.point(40, 40)
            });
        }
    }
});

let markers_without_image = L.markerClusterGroup({
    maxClusterRadius: 100,
    disableClusteringAtZoom: 15,
    showCoverageOnHover: false,
    iconCreateFunction: function (cluster) {
        var markers = cluster.getAllChildMarkers();
        if (markers.length < 10) {
            return L.divIcon({
                html: '<div class="red-cluster red-circle-tiny">' + markers.length + '</div>',
                iconSize: L.point(20, 20)
            });
        } else if (markers.length < 25) {
            return L.divIcon({
                html: '<div class="red-cluster red-circle-small">' + markers.length + '</div>',
                iconSize: L.point(25, 25)
            });
        } else if (markers.length < 50) {
            return L.divIcon({
                html: '<div class="red-cluster red-circle-normal">' + markers.length + '</div>',
                iconSize: L.point(30, 30)
            });
        } else if (markers.length < 250) {
            return L.divIcon({
                html: '<div class="red-cluster red-circle-big">' + markers.length + '</div>',
                iconSize: L.point(35, 35)
            });
        } else {
            return L.divIcon({
                html: '<div class="red-cluster red-circle-large">' + markers.length + '</div>',
                iconSize: L.point(40, 40)
            });
        }
    }
});

// Adding elements to the map
markers_with_image.addTo(map);

markers_without_image.addTo(map);

// Subgroup for the selected items
let markers_selected = L.featureGroup.subGroup();

// Making map fit to the state
map.fitBounds(bounds);

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// BUTTONS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
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

// Home
L.easyButton(
    "<i class='fa-solid fa-house'></i>",
    function () { window.open(home_url, '_self'); },
    homeTooltip
).addTo(map);

// Language
L.easyButton(
    "<i class='fa-solid fa-language'></i>",
    function () { $('#langModal').modal('show'); },
    langTooltip
).addTo(map);

// Group/Ungroup
L.easyButton({
    states: [
        {
            icon: "<i class='fa-solid fa-object-ungroup'></i> " + ungroupTitle,
            stateName: 'grouped',
            width: '100%',
            title: ungroupTooltip,
            onClick: function (btn, map) {
                btn.state('ungrouped');
                markers_with_image.freezeAtZoom("max");
                markers_without_image.freezeAtZoom("max");
            }
        },
        {
            icon: "<i class='fa-solid fa-object-group'></i> " + groupTitle,
            stateName: 'ungrouped',
            width: '100%',
            title: groupTooltip,
            onClick: function (btn) {
                btn.state('grouped');
                markers_with_image.freezeAtZoom(false);
                markers_without_image.freezeAtZoom(false);
            }
        }
    ]
}).addTo(map);

// Filter
let has_image_filtered = "all",
    types_filtered = "all";

L.easyButton({
    states: [
        {
            icon: "<i class='fa-solid fa-filter'></i> " + filterTitle,
            stateName: 'filter',
            width: '100%',
            title: filterTooltip,
            onClick: function (btn, map) {
                $('#has_image').val(has_image_filtered);
                $('#types').val(types_filtered);
                $('#filterModal').modal('show');
            }
        }]
}).addTo(map);

// Print
L.easyPrint({
    title: printTitle,
    position: 'topleft',
    sizeModes: ['A4Portrait', 'A4Landscape'],
    defaultSizeTitles: {A4Landscape: landscapeTitle, A4Portrait: portraitTitle}
}).addTo(map);

// Info
L.easyButton(
    '<i class="fa-solid fa-info"></i>',
    function () { $('#aboutModal').modal('show'); },
    infoTooltip
).addTo(map);

// Save Selection
var saveSelectButton = L.easyButton({
    states: [
        {
            icon: "<i class='fa-solid fa-download'></i> " + saveSelectionTitle,
            stateName: 'saveselect',
            width: '100%',
            display: 'none',
            title: selectTooltip,
            onClick: function (btn, map) {
                let selectedMarkers = [];
                markers_selected.getLayers().forEach(function (marker) {
                    const match = marker.getPopup().getContent().match(/.*(Q\d+).*/);
                    selectedMarkers.push(match[1]);
                });
                $.ajax({
                    url: "/print_selection",
                    type: "POST",
                    data: JSON.stringify({"items": selectedMarkers}),
                    contentType: "application/json",
                    dataType: "json",

                    success: function (response) {
                        var uri = 'data:text/csv;charset=UTF-8,' + encodeURIComponent(response);
                        var link = document.createElement('a');
                        link.download = 'route.csv';
                        link.href = uri;

                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    },
                    error: function (response) {
                        alert("Error");
                    }
                });
            }
        }
    ]
});

// Select
let toggle_select = false;

L.easyButton({
    states: [
        {
            icon: "<i class='fa-solid fa-map-location-dot'></i> " + selectTitle,
            stateName: 'select',
            width: '100%',
            title: selectTooltip,
            onClick: function (btn, map) {
                btn.state('unselect');
                toggle_select = !toggle_select;
                saveSelectButton.addTo(map);
            }
        },
        {
            icon: "<i class='fa-solid fa-map-location-dot''></i> " + selectTitle,
            stateName: 'unselect',
            width: '100%',
            title: unselectTooltip,
            onClick: function (btn, map) {
                btn.state('select');
                markers_selected.eachLayer(function (marker) {
                    if (marker.getIcon() === greenblueIcon) {
                        marker.setIcon(greenIcon);
                    } else if (marker.getIcon() === redblueIcon) {
                        marker.setIcon(redIcon);
                    }
                });
                toggle_select = !toggle_select;
                saveSelectButton.remove();
            }
        },
    ]
}).addTo(map);

// Geocoordinates
L.easyButton(
    '<i class="fa-solid fa-globe"></i>',
    function () { window.open(coordinates_url, '_self'); },
    coordinatesTooltip
).addTo(map);

// Suggest
L.easyButton(
    '<i class="fa-solid fa-comment-dots"></i>',
    function () { window.open(suggestions_url, '_self'); },
    suggestionsTooltip
).addTo(map);

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// FUNCTIONS AND ACTIONS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Function of each marker to change it when selected for making a route
function markerOnClick(e) {
    if (toggle_select) {
        e.target.closePopup();
        if (e.target.getIcon() === greenIcon) {
            e.target.setIcon(greenblueIcon);
            e.target.addTo(markers_selected);
        } else if (e.target.getIcon() === greenblueIcon) {
            e.target.setIcon(greenIcon);
            e.target.removeFrom(markers_selected);
        } else if (e.target.getIcon() === redIcon) {
            e.target.setIcon(redblueIcon);
            e.target.addTo(markers_selected);
        } else {
            e.target.setIcon(redIcon);
            e.target.removeFrom(markers_selected);
        }
        map.removeLayer(markers_selected);
    } else {}
}

// Removal of all layers and addition of selected layer. Has image and is of type target_layer
function removeOtherLayers(target_layer) {
    $.each([P1442, P1766, P18, P1801, P3311, P3451, P4291, P4640, P5252, P5775, P8517, P8592, P9721, P9906], function (index, layer) {
        map.removeLayer(layer);
    });
    map.addLayer(target_layer);
    let layerBounds = target_layer.getBounds();
    if (layerBounds.isValid()) { map.fitBounds(layerBounds, {padding: [20, 20]}); }
}

// Addition of all layers and removal of selected layer. Has no image of type target_layer
function removeThisLayer(target_layer) {
    $.each([P1442, P1766, P18, P1801, P3311, P3451, P4291, P4640, P5252, P5775, P8517, P8592, P9721, P9906], function (index, layer) {
        map.addLayer(layer);
    });
    map.removeLayer(target_layer);
}

// Filter function
$('#filter').on('click', function (event) {
    var has_image = $('#has_image').val(); // HAS IMAGE
    var types = $('#types').val(); // TYPES

    if (has_image === "yes") {
        map.removeLayer(markers_without_image);
        map.addLayer(markers_with_image);
        if (types === "all") {$.each([P1442, P1766, P18, P1801, P3311, P3451, P4291, P4640, P5252, P5775, P8517, P8592, P9721, P9906], function (index, layer) {map.addLayer(layer);});}
        else if (types === "P1442") {removeOtherLayers(P1442);}
        else if (types === "P1766") {removeOtherLayers(P1766);}
        else if (types === "P18") {removeOtherLayers(P18);}
        else if (types === "P1801") {removeOtherLayers(P1801);}
        else if (types === "P3311") {removeOtherLayers(P3311);}
        else if (types === "P3451") {removeOtherLayers(P3451);}
        else if (types === "P4291") {removeOtherLayers(P4291);}
        else if (types === "P4640") {removeOtherLayers(P4640);}
        else if (types === "P5252") {removeOtherLayers(P5252);}
        else if (types === "P5775") {removeOtherLayers(P5775);}
        else if (types === "P8517") {removeOtherLayers(P8517);}
        else if (types === "P8592") {removeOtherLayers(P8592);}
        else if (types === "P9721") {removeOtherLayers(P9721);}
        else if (types === "P9906") {removeOtherLayers(P9906);}
    } else if (has_image === "no") {
        map.addLayer(markers_without_image);
        map.addLayer(markers_with_image);
        if (types === "all") {$.each([P1442, P1766, P18, P1801, P3311, P3451, P4291, P4640, P5252, P5775, P8517, P8592, P9721, P9906], function (index, layer) {map.removeLayer(layer);});}
        else if (types === "P1442") {removeThisLayer(P1442);}
        else if (types === "P1766") {removeThisLayer(P1766);}
        else if (types === "P18") {removeThisLayer(P18);}
        else if (types === "P1801") {removeThisLayer(P1801);}
        else if (types === "P3311") {removeThisLayer(P3311);}
        else if (types === "P3451") {removeThisLayer(P3451);}
        else if (types === "P4291") {removeThisLayer(P4291);}
        else if (types === "P4640") {removeThisLayer(P4640);}
        else if (types === "P5252") {removeThisLayer(P5252);}
        else if (types === "P5775") {removeThisLayer(P5775);}
        else if (types === "P8517") {removeThisLayer(P8517);}
        else if (types === "P8592") {removeThisLayer(P8592);}
        else if (types === "P9721") {removeThisLayer(P9721);}
        else if (types === "P9906") {removeThisLayer(P9906);}
    } else {
        map.addLayer(markers_without_image);
        map.addLayer(markers_with_image);
        $.each([P1442, P1766, P18, P1801, P3311, P3451, P4291, P4640, P5252, P5775, P8517, P8592, P9721, P9906, markers_without_image], function (index, layer) {
            map.addLayer(layer);
        });
    }

    let layerBounds = layer_to_preserve.getBounds();
            if (layerBounds.isValid()) {
                map.fitBounds(layerBounds, {padding: [20, 20]});
            }

    has_image_filtered = has_image;
    types_filtered = types;
});

// Update of form fields
$('#has_image').on('change', function () {
    if (this.value === "all") {
        $('#types').prop("disabled", true);
    } else if (this.value === "no") {
        $('#types').prop("disabled", false);
        $("#types option[value='all']").text(noTypeTitle);
    } else {
        $('#types').prop("disabled", false);
        $("#types option[value='all']").text(allTypesTitle);
    }
    $('#types option[value="select"]').prop("selected", true);
});

// Create subgroups
let P1442 = L.featureGroup.subGroup(markers_with_image).addTo(map),
    P1766 = L.featureGroup.subGroup(markers_with_image).addTo(map),
    P18 = L.featureGroup.subGroup(markers_with_image).addTo(map),
    P1801 = L.featureGroup.subGroup(markers_with_image).addTo(map),
    P3311 = L.featureGroup.subGroup(markers_with_image).addTo(map),
    P3451 = L.featureGroup.subGroup(markers_with_image).addTo(map),
    P4291 = L.featureGroup.subGroup(markers_with_image).addTo(map),
    P4640 = L.featureGroup.subGroup(markers_with_image).addTo(map),
    P5252 = L.featureGroup.subGroup(markers_with_image).addTo(map),
    P5775 = L.featureGroup.subGroup(markers_with_image).addTo(map),
    P8517 = L.featureGroup.subGroup(markers_with_image).addTo(map),
    P8592 = L.featureGroup.subGroup(markers_with_image).addTo(map),
    P9721 = L.featureGroup.subGroup(markers_with_image).addTo(map),
    P9906 = L.featureGroup.subGroup(markers_with_image).addTo(map);
