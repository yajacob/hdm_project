function copyClipBoard(ctext) {
	var copyFrom = $('<textarea/>');
	copyFrom.css({
		position: "absolute",
		left: "-1000px",
		top: "-1000px",
	});
	copyFrom.text(ctext);
	$('body').append(copyFrom);
	copyFrom.select();
	document.execCommand('copy');
	alert("URL copied to clipboard.\n\n"+ctext);
}
