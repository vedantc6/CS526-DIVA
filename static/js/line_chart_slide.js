
// Themes begin
//am4core.useTheme(am4themes_material);
//am4core.useTheme(am4themes_animated);
// Themes end

// Create chart instance
var chart = am4core.create("chartdiv", am4charts.XYChart);



function generateChartData2(Jdata) {
	var chartData2 = [];
	 
	 for (var i = 0; i < Jdata.length; i++)
		 chartData2.push({
            date: Jdata[i].year,
            visits: Jdata[i].value
        });
		 
		 
		//  console.log('Output: ', chartData2);
		 

// Add data
chart.data =chartData2; //generateChartData();


var dateAxis = chart.xAxes.push(new am4charts.DateAxis());
dateAxis.renderer.minGridDistance = 50;

var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());

// Create series
var series = chart.series.push(new am4charts.LineSeries());
series.dataFields.valueY = "visits";
series.dataFields.dateX = "date";
series.strokeWidth = 2;
series.minBulletDistance = 10;
series.tooltipText = "{valueY}";
series.tooltip.pointerOrientation = "vertical";
series.tooltip.background.cornerRadius = 20;
series.tooltip.background.fillOpacity = 0.5;
series.tooltip.label.padding(12,12,12,12)

// Add scrollbar
chart.scrollbarX = new am4charts.XYChartScrollbar();
chart.scrollbarX.series.push(series);

// Add cursor
chart.cursor = new am4charts.XYCursor();
chart.cursor.xAxis = dateAxis;
chart.cursor.snapToSeries = series;

		 return chartData2;
		 
}


fetch('http://127.0.0.1:5000/line_chart_data')
    .then(res => res.json())
    .then((out) => {
		generateChartData2(out);
		// console.log(out[0].year + " " + out[0].value);
       
}).catch(err => console.error(err));
