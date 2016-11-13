function plot_radar(dpid) {
  var api_url = "http://" + window.location.hostname + ":8181/kytos/stats/" +
    dpid + "/ports";
  $.ajax({
    dataType: "json",
    url: api_url,
    success: function(reply) {
      rx = [];
      tx = [];
      if ('data' in reply) {
        for (var i in reply.data) {
          info = reply.data[i];
          rx.push({'value': info.rx_utilization * 100,
                   'speed': info.speed});
          tx.push({'value': info.tx_utilization * 100,
                   'speed': info.speed});
        }
      }
      radar_data = [rx, tx];
      RadarChart("#switchChart", radar_data);
    }
  });
}

function get_switch_flows(data, callback) {
  var api_url = "http://" + window.location.hostname + ":8181/kytos/stats/" +
    data.dpid + "/flows";
    $.ajax({
      dataType: "json",
      url: api_url,
      success: function(reply) {
        data.flows = [];
        if ('data' in reply) {
          for (var i in reply.data) {
            flow = reply.data[i];
            data.flows.push({'id': flow.id.substring(0, 7),
                             'Bps': flow.stats.Bps.toFixed(2),
                             'pps': flow.stats.pps.toFixed(2)});
          }
        }
        callback(data);
      }
    });
};
