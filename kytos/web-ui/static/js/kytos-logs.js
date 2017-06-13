var socket = io();
var channels = new Set();

;(function() {
  var max_lines = 50;
  var ws_led = $('#statusicons .websocket-status')

  socket.on('connect', on_connect);
  socket.on('disconnect', on_disconnect);
  socket.on('show logs', update_log);

  function on_connect() {
    console.log('Socket connected.');
    // restore channel subscriptions
    for (let channel of channels) {
      join_channel(channel, true);
    }
    ws_led.addClass('status-online')
          .removeClass('status-offline');
  }

  function on_disconnect() {
    console.log('Socket disconnected.');
    ws_led.removeClass('status-online')
          .addClass('status-offline');
  }

  function update_log(new_lines) {
    // Remove some lines if more than max_lines
    var old_lines = $('#tab_logs .log_message');
    var total_lines = old_lines.length + new_lines.length;

    if (total_lines > max_lines) {
      var excess = total_lines - max_lines;
      $('#tab_logs .log_message').slice(0, excess).remove();
    }

    // Format log lines
    var formatted = new_lines.map(function(line) {
      return $('<div/>', {
        text: line,
        class: 'log_message controller'
      });
    });

    $('#tab_logs').append(formatted)
                  .scrollTop($('#tab_logs')[0].scrollHeight);
  }
}());

function join_channel(channel, force = false) {
  if (socket.connected && (!channels.has(channel) || force)) {
     socket.emit('join', channel, function() {
       channels.add(channel);
       console.log('Subscribed to ' + channel);
     });
  }
  console.log('Subscriptions: ' + channels);
}

function leave_channel(channel) {
  if (channels.has(channel) && socket.connected) {
     socket.emit('leave', channel, function() {
       channels.delete(channel);
       console.log('Unsubscribed from ' + channel);
     });
  }
  console.log('Subscriptions: ' + channels);
}

function toggle_log(enabled) {
  channel = 'log';
  enabled ? join_channel(channel) : leave_channel(channel);
}
