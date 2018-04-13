var completes = [];
var stations = [];
$(document).ready(function(){
     $.ajax({
           type: "GET",
           url: "/api/station/all",
           contentType: "application/json",
           dataType: "json",
           success: function(result){
               for (var i in result){
                   completes.push(result[i].name);
               }
               $("#inputNameStation").autocomplete({
                   source: completes
                });
           },
           error: function(result){
               alert(result.responseJSON.message);
           }
    });


    $("#add-station-button").on("click", function(){
        var stationName = $("#inputNameStation").val();
        var stationDistance = $("#inputDistanceStation").val();

        if(stationName === "" || stationDistance === ""){
            alert("All fields are required!");
            return;
        }

        var nextStation = {
            "name": stationName,
            "dist": parseFloat(stationDistance)
        };

        stations.push(nextStation);
        var tableRow = "<tr><td>"+
            nextStation.name + "</td><td>" + nextStation.dist + "</td>" +
            "<td><button class='btn btn-danger remove-button' id='" + stations.length + "'>Remove</button>"
            +"</td></tr>";

        $("#waiting-pairs tbody").append(tableRow);
    });

    $("#waiting-pairs").on("click", ".btn.btn-danger.remove-button", function(event){
       var station_id = parseInt(event.target.id);
       stations.splice(station_id-1,1);
       $(this).closest('tr').remove();
    });

    $("#add-line-button").on("click", function(){
        var lineName = $("#inputLineName").val();
        var lineDesc = $("#inputLineDescription").val();
        var lineColor = $("#inputLineColor").val();

        if(lineName === "" || lineDesc === "" || lineColor === "" || stations.length < 2){
            alert("All fields are required, make sure that you have at least 2 stations in list!");
            return;
        }

        lineColor = lineColor.substr(1);

        var lineInformation = {
            "line": lineName,
            "desc": lineDesc,
            "color": lineColor,
            "stations": stations
        };

        $.ajax({
           type: "POST",
           url: "/api/line",
           data: JSON.stringify(lineInformation),
           contentType: "application/json",
           dataType: "json",
           success: function(result){
               alert(result.message);
               window.location.replace("/addline");
           },
           error: function(result){
               alert(result.responseJSON.message);
           }
       });
    });

});