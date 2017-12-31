function searchfunction() {
    var input, filter, table, tr, td, i;
    input = document.getElementById("inputSearchStation");
    filter = input.value.toUpperCase();
    table = document.getElementById("tableStation");
    tr = table.getElementsByTagName("tr");

    for(i = 0; i < tr.length; i++){
      td = tr[i].getElementsByTagName("td")[0];
      if(td){
        if(td.innerHTML.toUpperCase().indexOf(filter) > -1){
          tr[i].style.display = "";
        }else {
          tr[i].style.display = "none";
        }
      }
    }
}

function searchoptions() {
	var input, filter, fselect, ovalue, i;
	input = document.getElementById("inputSearchStation");
	filter = input.value.toUpperCase();
	fselect = document.getElementById("MasterSelectBox");
	
	for(i = 0; i < fselect.length; i++){
		ovalue = fselect.options[i].innerHTML;
		if(ovalue.toUpperCase().indexOf(filter) > -1){
			fselect.options[i].style.display = "";
		}else {
			fselect.options[i].style.display = "none";
		}
	}
}