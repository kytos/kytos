;(function() {
  console.log("kytos-logs started")
  var $logs = $("#tab_logs").text('')
  // Method used to request a websocket and append in tab_logs terminal.
  function LogWebSocketReceive()
  {
     if ("WebSocket" in window)
     {
        var ws = new WebSocket("ws://localhost:8765");

        ws.onmessage = function (evt)
        {
           var received_msg = evt.data;
           received_msg = received_msg.replace(/\n/g,'<br>')
           $logs.append(received_msg)
        };
     }
     else
     {
        console.log("WebSocket NOT supported by your Browser!");
     }
  }

  setInterval(function(){ LogWebSocketReceive() }, 2000);
}());
