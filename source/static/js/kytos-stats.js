function plot_context_radar(ifaces) {
  rx = [];
  tx = [];
  for (var i in ifaces) {
    iface = ifaces[i];
    if (iface.speed != "") {
      rx.push({'value': iface.rx_util,
               'speed': iface.speed});
      tx.push({'value': iface.tx_util,
               'speed': iface.speed});
    }
  }
  radar_data = [rx, tx];
  RadarChart("context-switchChart", radar_data);
}

function add_switch_interfaces(data, callback1, callback2) {
    $.ajax({
      dataType: "json",
      url: api_stats + data.dpid + '/ports',
      success: function(reply) {
        ifaces = [];
        if ('data' in reply) {
          for (var i in reply.data) {
            iface = reply.data[i];
            info = {name: iface.name, port: iface.port, mac: iface.mac}
            if (iface.speed !== null) {
              info.rx_util = (iface.rx_util * 100).toFixed(2);
              info.tx_util = (iface.tx_util * 100).toFixed(2);
              info.speed = iface.speed / Math.pow(10, 9);
            } else {
              info.rx_util = "";
              info.tx_util = "";
              info.speed = "";
            }
            ifaces.push(info);
          }
        }
        data.interfaces = ifaces;
        callback1(data, callback2);
      }
    });
}

function add_switch_flows(data, callback) {
    $.ajax({
      dataType: "json",
      url: api_stats + data.dpid + '/flows',
      success: function(reply) {
        flows = [];
        if ('data' in reply) {
          for (var i in reply.data) {
            flow = reply.data[i];
            flows.push({'id': flow.id.substring(0, 7),
                        'Bps': flow.stats.Bps.toFixed(2),
                        'pps': flow.stats.pps.toFixed(2)});
          }
        }
        data.flows = flows;
        callback(data);
      }
    });
}

function add_stats(data, callback) {
  add_switch_interfaces(data, add_switch_flows, callback);
}
