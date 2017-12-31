function moveUp() {
	var selectList = document.getElementById("PairedSelectBox");
	var selectOptions = selectList.getElementsByTagName('option');
	for (var i = 1; i < selectOptions.length; i++) {
		var opt = selectOptions[i];
		if (opt.selected) {
			selectList.removeChild(opt);
			selectList.insertBefore(opt, selectOptions[i - 1]);
		}
       }
}

function moveDown() {
	var selectList = document.getElementById("PairedSelectBox");
	var selectOptions = selectList.getElementsByTagName('option');
	for (var i = selectOptions.length - 2; i >= 0; i--) {
		var opt = selectOptions[i];
		if (opt.selected) {
		   var nextOpt = selectOptions[i + 1];
		   opt = selectList.removeChild(opt);
		   nextOpt = selectList.replaceChild(opt, nextOpt);
		   selectList.insertBefore(nextOpt, opt);
		}
       }
}
