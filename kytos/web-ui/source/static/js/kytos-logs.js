;(function() {
  console.log("kytos-logs started")

  var connected=false;
  var current_line = 0;
  var socket = io.connect('http://localhost:8181/logs');

  socket.on('connect', function(){
    turn_on_led()
    connected = true;
    console.log('connected')
    request_log_changes()
  })

  socket.on('start logs', function(data){
    if ($('#enable_log')[0].checked)
    {
      received_msgs = data.buff
      current_line = data.last_line

      $.each(received_msgs, function(index, msg){
        add_log_message(msg, 'controller')
      });
    }
  })

  socket.on('connect_error',function(){
    connected = false;
    turn_off_led()
    console.log('error');
  })

  socket.on('disconnect', function(data) {
    connected = false;
    turn_off_led()
    console.log('disconnected')
  })

  socket.on('show logs', function(data){
    if ($('#enable_log')[0].checked)
    {
      received_msgs = data.buff
      current_line = data.last_line

      $.each(received_msgs, function(index, msg){
        add_log_message(msg, 'controller')
      });
    }
  })

  var ws_led = $('.nav.sidebar .websocket-status')

  function turn_on_led(){
    ws_led.addClass('status-online');
    ws_led.removeClass('status-offline');
  }

  function turn_off_led(data){
      ws_led.removeClass('status-online');
      ws_led.addClass('status-offline');
  }

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

  function request_log_changes(){
    if (connected)  socket.emit('show logs', {"current_line": current_line})
  }
  setInterval(request_log_changes, 3000)
}());

