// let map;
// function initMap() {
//     const map = new google.maps.Map(document.getElementById("map"), {
//         zoom: 6,
//         center: {lat: 52.721246, lng: 41.452238},
//     });
//
//     let geoJsonData;
//     fetch('http://127.0.0.1:8000/get_initial_dataset')
//         .then((response) => {
//             return response.json();
//         })
//         .then((data) => {
//             geoJsonData = JSON.parse(data);
//             map.data.addGeoJson(geoJsonData);
//         });
//
//     map.data.setStyle({strokeColor: "blue"});
//     return map;
// }
//
// map = initMap();
//
// function loadGeoJson() {
//     let textArea = $('#jsonTextArea').val();
//     map.data.addGeoJson(textArea);
// }

let map;

function initMap() {
    // set up the map
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 6,
        center: {lat: 52.721246, lng: 41.452238},
    });
}

function loadGeoJsonString(geoString) {
    try {
        console.log(geoString);
        const geojson = JSON.parse(geoString);
        map.data.addGeoJson(geojson);
    } catch (e) {
        alert("Not a GeoJSON file!");
    }
    zoom(map);
}

/**
 * Update a map's viewport to fit each geometry in a dataset
 */
function zoom(map) {
    const bounds = new google.maps.LatLngBounds();
    map.data.forEach((feature) => {
        processPoints(feature.getGeometry(), bounds.extend, bounds);
    });
    map.fitBounds(bounds);
}

/**
 * Process each point in a Geometry, regardless of how deep the points may lie.
 */
function processPoints(geometry, callback, thisArg) {
    if (geometry instanceof google.maps.LatLng) {
        callback.call(thisArg, geometry);
    } else if (geometry instanceof google.maps.Data.Point) {
        callback.call(thisArg, geometry.get());
    } else {
        geometry.getArray().forEach((g) => {
            processPoints(g, callback, thisArg);
        });
    }
}

/* DOM (drag/drop) functions */
function initEvents() {
    [...document.getElementsByClassName("file")].forEach((fileElement) => {
        fileElement.addEventListener(
            "dragstart",
            (e) => {
                e.dataTransfer.setData(
                    "text/plain",
                    JSON.stringify(files[Number(e.target.dataset.value)])
                );
                console.log(e);
            },
            false
        );
    });
    // set up the drag & drop events
    const mapContainer = document.getElementById("map");
    mapContainer.addEventListener("dragenter", addClassToDropTarget, false);
    mapContainer.addEventListener("dragover", addClassToDropTarget, false);
    mapContainer.addEventListener("drop", handleDrop, false);
    mapContainer.addEventListener("dragleave", removeClassFromDropTarget, false);
}

function addClassToDropTarget(e) {
    e.stopPropagation();
    e.preventDefault();
    document.getElementById("map").classList.add("over");
    return false;
}

function removeClassFromDropTarget(e) {
    document.getElementById("map").classList.remove("over");
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    removeClassFromDropTarget(e);
    const files = e.dataTransfer.files;

    if (files.length) {
        // process file(s) being dropped
        // grab the file data from each file
        for (let i = 0, file; (file = files[i]); i++) {
            const reader = new FileReader();

            reader.onload = function (e) {
                loadGeoJsonString(reader.result);
            };

            reader.onerror = function (e) {
                console.error("reading failed");
            };
            reader.readAsText(file);
        }
    } else {
        // process non-file (e.g. text or html) content being dropped
        // grab the plain text version of the data
        const plainText = e.dataTransfer.getData("text/plain");
        console.log(plainText);

        if (plainText) {
            loadGeoJsonString(plainText);
        }
    }
    // prevent drag event from bubbling further
    return false;
}

let files = [];

function getInitialDataset() {
    fetch('http://127.0.0.1:8000/get_initial_dataset')
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            files.push(JSON.parse(data));
        });
}


function initialize() {
    getInitialDataset();
    initMap();
    initEvents();
}


