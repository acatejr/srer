
$(document).ready(function() {
    var theMap = L.map('themap').setView([31.8197497,-110.8742436], 10.5)
    var accessToken = "pk.eyJ1IjoiYWNhdGVqciIsImEiOiJDTFpxOWpJIn0.1gwlWR5IcLfCAbBs0Ue27g"
    var rainGages = [];

    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiYWNhdGVqciIsImEiOiJDTFpxOWpJIn0.1gwlWR5IcLfCAbBs0Ue27g', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        maxZoom: 18,
        id: 'mapbox.streets',
        accessToken: accessToken
    }).addTo(theMap)

    var baseUrl = "http://127.0.0.1:8000/api/graphql?query="
    var raingageQry = "{ raingages { edges { node { id latitude longitude code name } } } }"

    $.getJSON(baseUrl + raingageQry)
        .done( function(response) {
            response.data.raingages.edges.forEach(function(g) {
                var coords = [g.node.latitude, g.node.longitude]
                var markerAttributes = {
                    title: g.node.name
                }
                var marker = L.marker(coords, markerAttributes).addTo(theMap)
                marker.bindPopup(markerPopup(g))

        })
    })

    $('body').on('click', '.gage-popup', function (e) {
        $('#gage-name').html('').html('Gage: ' + $(this).data('name'))
        return false
    })

    function markerPopup(gage) {
        var html = ""
        html += "<div><a id='" + gage.node.id + "' href='#' class='gage-popup' data-name='" + gage.node.name + "'>" + gage.node.name + "</a></div>"
        html += "<div>Latitude: " + gage.node.latitude + "</div>"
        html += "<div>Latitude: " + gage.node.longitude + "</div>"
        return html
    }

})
