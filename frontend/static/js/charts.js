const charts = JSON.parse(document.querySelector('#chart-data').textContent);
document.querySelectorAll('.metric-chart').forEach((canvas,index) => {
  const [label,labels,data] = charts[index];
  new Chart(canvas, {
    type: 'bar',
    data: {labels, datasets: [{label, data, backgroundColor: '#365de7'}]},
    options: {responsive:true, legend:{display:false}, scales:{yAxes:[{ticks:{beginAtZero:true,precision:0}}]}}
  });
});
