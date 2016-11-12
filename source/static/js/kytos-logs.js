;(function() {
  console.log("kytos-logs started")
  // Method used to request a websocket and append in tab_logs terminal.
  ws_led = $('.nav.sidebar .websocket-status');

  function LogWebSocketReceive() {
    if ("WebSocket" in window) {
      var ws = new WebSocket(log_server_url)
      console.log(ws.readyState);
      ws.onopen = function(evt) {
        ws_led.addClass('status-online');
        ws_led.removeClass('status-offline');
      };
      ws.onerror = function(evt) {
        ws_led.removeClass('status-online');
        ws_led.addClass('status-offline');
      }
      if ($('#enable_log')[0].checked) {
        ws.onmessage = function (evt) {
          var received_msgs = evt.data;
          $.each(received_msgs.split('\n'), function(index, msg) {
            if (msg) { add_log_message(msg, 'controller')}
          })
        };
      }
    } else {
      //console.log("WebSocket NOT supported by your Browser!");
      $('#enable_log').prop('checked', false).change();
      ws_led.removeClass('status-online status-offline')
    }
  }

  setInterval(LogWebSocketReceive, 2000);

  function resize_log_tab() {
    $('#tab_logs').height($('.terminal-body').height() - 25);
  }

  $('#tab_logs').on('resize', resize_log_tab).trigger('resize');

}());

function add_log_message(msg, src_tag) {
  if ($('#tab_logs div.log_message').length >= 500) {
    $('#tab_logs').find('#tab_logs:first').remove();
  }
  $('<div/>', {
      text: msg,
      "class": 'log_message ' + src_tag
  }).appendTo('#tab_logs');
  $('#tab_logs').scrollTop($('#tab_logs').get(0).scrollHeight);
}
