var stations = [];
var dialog = null;
function editStation(){
    var toUpdate = [];
    var originalStationName = $("#originalStationName").val();
    console.log(originalStationName);
    var newStationName = $("#inputStationName").val();
    var newLocation = $("#inputStationLocation").val();

    if(originalStationName.length <= 0 || newStationName.length <= 0 || newLocation.length <= 0){
        alert("All fields are required!");
        return;
    }


    var location = newLocation.split(",");
    var latitude = parseFloat(location[0]);
    var longitude = parseFloat(location[1]);
    var updateValues = {
            "oldname": originalStationName,
            "newname": newStationName,
            "latitude": latitude,
            "longitude": longitude
    };
    toUpdate.push(updateValues);
    console.log(toUpdate);

    $.ajax({
        type: 'PUT',
        url: '/api/station',
        contentType: 'application/json',
        data: JSON.stringify(toUpdate),
        dataType: 'json',
        success: function(result){
            alert(result.message);
            window.location.replace("/liststation");
        },
        error: function(result){
            alert(result.responseJSON.message);
        }
    });
}

$(document).ready(function(){
    dialog = $( "#dialog-form" ).dialog({
        autoOpen: false,
        height: 400,
        width: 350,
        modal: true,
        buttons: {
            "Save": editStation,
            Cancel: function() {
                dialog.dialog("close");
            }
        }
    });

    $.ajax({
           type: "GET",
           url: "/api/station/all",
           contentType: "application/json",
           dataType: "json",
           success: function(result){
               stations=result;
               for (var station in stations){
                    var get_station = stations[station];

                    var tableRow = "<tr><td>" +
                    get_station.name+"</td><td><a href='https://www.google.com/maps/?q=" +
                    get_station.latitude + "," + get_station.longitude +
                    "' target='_blank'>" +
                    get_station.latitude + "," + get_station.longitude +
                    "</a></td><td><button class='btn btn-danger delete-button' id='"+ get_station.name +"'>Delete</button>"+
                        "<button class='btn btn-default edit-button' id='"+ get_station.name +"'>Edit</button></td></tr>";

                    $("#table-stations tbody").append(tableRow);
                }
           },
           error: function(result){
               alert(result.responseJSON.message);
           }
    });


    $("#table-stations").on("click", ".btn.btn-danger.delete-button", function(event){
        var station_name = event.target.id;
        var station = null;
        var station_id = null;
        for(var i in stations){
            if(stations[i].name === station_name){
                station_id = i;
                station = stations[i];
                break;
            }
        }
        if(station === null || station_id === null)
            return;

        if(confirm("Are sure to delete station " + station.name + "? After deletion line connections will also be deleted, you need to reconfigure them.")){
            var ths = $(this);
            var toDelete = [];
            toDelete.push(station.name);
            $.ajax({
                type: 'DELETE',
                url: '/api/station',
                contentType: 'application/json',
                data: JSON.stringify(toDelete),
                dataType: 'json',
                success: function(result){
                    alert(result.message);
                    stations.splice(station_id, 1);
                    ths.closest('tr').remove();
                },
                error: function(result){
                    alert(result.responseJSON.message);
                }
            });

        }
    });

    $( "#table-stations" ).on( "click", ".btn.btn-default.edit-button", function(event) {
        $("#originalStationName").val(event.target.id);
        $("#inputStationName").val(event.target.id);

        for(var station in stations){
            if(stations[station].name === event.target.id){
                $("#inputStationLocation").val(stations[station].latitude + "," + stations[station].longitude);
                break;
            }
        }

        dialog.dialog("open");
    });

    $("#inputSearchStation").on("keyup", function() {
        var value = $(this).val().toUpperCase();

        $("#table-stations tr").each(function(index) {
            if (index !== 0) {

                $row = $(this);

                var id = $row.find("td:first").text().toUpperCase();

                if (id.indexOf(value) !== 0) {
                    $row.hide();
                }
                else {
                    $row.show();
                }
            }
        });
    });

});