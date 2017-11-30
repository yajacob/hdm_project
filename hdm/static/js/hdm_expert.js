function fnRestartEvaluation() {
	if(confirm("Do you want to restart this evaluation?")) {
		location.reload();
	}
}

function fnResetSlide() {
	$(".slidebar").val(50);
	$(".irs-bar").css("width", "50%");
	$(".irs-slider").css("left", "50%");
	$(".irs-single").css("left", "50%");
	$(".irs-single").text("50%");
}

function showValue(id, newValue)
{
	$("#rs_range"+id).val(newValue);
	$("#ls_range"+id).val(100 - newValue);
}

//When clicking item for evaluating 
function fnEval(id) {
	if($("#"+id).hasClass("disabled")) {
		alert("You already evaluated this item.\n\nThank you.");
		return;
	}
	
	if(id.length != 4) return;
	cr_code = parseInt(id.substring(2,3));
	fa_code = parseInt(id.substring(3,4));

	$("#cur_eval_item").val(id);
	var hdm_cr = $("#hdm_criteria").val(); 
	var hdm_fa = $("#hdm_factors").val(); 
	var hdm_al = $("#hdm_alternatives").val();
	
	ob_arr = hdm_cr.split(",");
	cr_arr = hdm_fa.split("|");
	al_arr = hdm_al.split(",");

	var item_size = 0;
	var item_arr;
	// case: hdm_criteria
	if(id=="CR00") {
		item_arr = ob_arr;
		item_size = item_arr.length;
		$("#eval_title").text("Evaluation: Criteria");
	}
	// case: hdm_factors
	else if(fa_code == "0") {
		item_arr = cr_arr[cr_code-1].split(",");
		item_size = item_arr.length;
		$("#eval_title").text("Evaluation: Factor / " + ob_arr[cr_code-1]);
	}
	// case: hdm_alternatives
	else {
		item_arr = al_arr;
		item_size = item_arr.length;
		fa_arr = cr_arr[cr_code-1].split(",");
		$("#eval_title").text("Evaluation: Alternatives / " + fa_arr[fa_code-1]);
	}

	var k = 1;
	var ls_dcode = "";
	var rs_dcode = "";

	$(".div_eval").hide();
	for(i=0; i<item_size; i++) {
		m = i+1;
		if(id=="CR00") ls_dcode = "CR"+m+"0";
		else if(fa_code == "0") ls_dcode = "CR"+cr_code+m;
		//else ls_dcode = "AL"+m+"0";
		else ls_dcode = id+m;
		ls_item = item_arr[i].trim();
		for(j=i+1; j<item_size; j++) {
			if(id=="CR00") rs_dcode = "CR"+(j+1)+"0";
			else if(fa_code == "0") rs_dcode = "CR"+cr_code+(j+1);
			else rs_dcode = id + (j+1);

			rs_item = item_arr[j].trim();
			$("#td_ls_item"+k).text(ls_item);
			$("#td_rs_item"+k).text(rs_item);
			$("#div_eval"+k).show();

			// Set data-code
			$("#ls_range"+k).attr("data-code", ls_dcode);
			$("#rs_range"+k).attr("data-code", rs_dcode);

			showValue(k, 50);
			k++;
		}
	}
	$("#cur_eval_item_cnt").val(k-1);
	$('#sbModal').modal('show');
}

