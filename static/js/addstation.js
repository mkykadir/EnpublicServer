
var stations = [];
$(document).ready(function(){
    function addStationsList(get_station){
        stations.push(get_station);
        var tableRow = "<tr><td>" +
            get_station.name+"</td><td><a href='https://www.google.com/maps/?q=" +
            get_station.latitude + "," + get_station.longitude +
            "' target='_blank'>" +
            get_station.latitude + "," + get_station.longitude +
            "</a></td><td><button class='btn btn-danger remove-button' id='"+ stations.length +"'>Remove</button></td></tr>";

        $("#waiting-stations tbody").append(tableRow);
    }

    $("#waiting-stations").on("click", ".btn.btn-danger.remove-button", function(event){
        var station_id = parseInt(event.target.id);
        stations.splice(station_id-1, 1);
        $(this).closest('tr').remove();
    });

    $("#add-single-station").on("click", function(){
       var stationName = $("#inputStationName").val();
       var stationLocation = $("#inputStationLocation").val();
       var location = stationLocation.split(",");
       var latitude = parseFloat(location[0]);
       var longitude = parseFloat(location[1]);

       if(stationName === "" || stationLocation === ""){
           alert("All fields are required!");
           return;
       }

       var newStation = {
           "name": stationName,
           "latitude": latitude,
           "longitude": longitude
       };

       var stationExist;
       for(var i in stations){
           if(stations[i].name === stationName){
               stationExist = true;
           }
       }
       if(!stationExist){
           addStationsList(newStation);
       }else{
           // station exists warn user!
           alert("Station already exists, change name of the station!");
       }
    });

    $("#add-all-stations").on("click", function(){
       var stations_length = $("#waiting-stations tbody tr").length;
       if(stations_length <= 0){
           alert("Add at least one station!");
           return;
       }

       console.log(stations);
       $.ajax({
           type: "POST",
           url: "/api/station",
           data: JSON.stringify(stations),
           contentType: "application/json",
           dataType: "json",
           success: function(result){
               alert(result.message);
               window.location.replace("/addstation");
           },
           error: function(result){
               alert(result.responseJSON.message);
           }
       });
    });
});