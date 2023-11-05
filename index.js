
fetch('222222 40.596108-105.140583_graph.csv')
	.then(function (response) {
		return response.text();
	})
  .then(function (text) {
    let series = csvToSeries(text);
    renderChart(series);
  })
	.catch(function (error) {
		//Something went wrong
		console.log(error);
	});

//arrays for each line
let data = [];
let actual = [];
let predicted = [];
let upper = [];

function csvToSeries(text) {
	
	let dataAsJson = JSC.csv2Json(text);

	dataAsJson.forEach(function (row) {

        //push values from file to array
				actual.push({x: (row.x/60), y: row.actual});
        predicted.push({x: (row.x/60), y: row.predicted});
        upper.push(row.upper);
        
	});

  
  
  //graph the lines
	return [
		{name: 'Points', points: actual},
		{name: 'Numbers', points: predicted}, 
    {name: 'Top', points: upper},
	];
}


function renderChart(series){

  let max = upper.length/60;
  
  for (let i = 0; i < max; i++) {
      let high = (upper[i] + 1);
      let low = 0;

      data.push({x: i, y: [high, low]});
     
  }
  
  
   var chart = JSC.Chart('chartDiv', {
     debug: true,
     type: 'area_spline',
     defaultPoint_marker_visible: false,
     palette: ['crimson', '#03bbfb'],

     yAxis: [
       {
         id: 'mainY',
         label_text: 'Change in Concentration',
         defaultTick: { label: { text: '%value' } },
         scale: {
            range: [0, 200]
          }
       }
     ],
     xAxis: [
       {
       id: 'mainX',
       label_text: 'Hours',
       crosshair_enabled: true,
       formatString: 'MMM',
     }
    ],

     defaultSeries_shape_opacity: 0.7,
     
     series: [
       {name: 'Expected Range', points: data},
       {name: 'Actual', type: 'line', points: actual},
       {name: 'Predicted', type: 'line', points: predicted}
     ]
     
   });
  
}



