  function drawChart(chart_id, row_dat) {
	// Create the data table.
	var data = new google.visualization.DataTable();
	data.addColumn('string', 'Topping');
	data.addColumn('number', 'Slices');
	data.addRows(row_data);
	//data.addRows([['Color', 96],['Delivery', 66],['Memory', 138],]);
	
	var options = {
	  title: 'Criteria'
	};
	
	alert("chart_id:"+chart_id);
	alert("row_dat:"+row_dat);
	
	#var chart = new google.visualization.PieChart(document.getElementById('piechart'));
	#var chart = new google.visualization.PieChart(document.getElementById(char_id));
	var chart = new google.visualization.PieChart($("#"+chart_id));
	
	chart.draw(data, options);
}
