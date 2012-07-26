// needs node.js 
// npm socket.io
// npm amqp
// rabbitmq running at localhost 

var http = require('http'),
	url = require('url'),
	fs = require('fs'),
    io = require('socket.io'),
	amqp = require('amqp'),
	sys = require(process.binding('natives').util ? 'util' : 'sys');


send404 = function(res){
  res.writeHead(404);
  res.write('404');
  res.end();
};



server = http.createServer(function(req, res){ 
 // your normal server code 
  var path = url.parse(req.url).pathname;
  switch (path){
	//case '/json.js':
	case '/':
	fs.readFile(__dirname + "/index.html", function(err, data){
        if (err) return send404(res);
        res.writeHead(200, {'Content-Type': path == 'json.js' ? 'text/javascript' : 'text/html'})
        res.write(data, 'utf8');
        res.end();
      });
      break;
 }
 	
});
server.listen(8080);

// socket.io
var socket = io.listen(server); 
// ampq
var connection = amqp.createConnection({ host: '127.0.0.1' });

connection.addListener('ready', function(){
  var queue = connection.queue('stockQueue')
  // create the exchange if it doesnt exist
  var exchange = connection.exchange('stockExchange')
  queue.bind("stockExchange", "key.a");
  
  socket.on('connection', function(client){ 
	  //client.broadcast({ announcement: client.sessionId + ' connected'  });
	  client.on('message', function(message){
		console.log(message);
		//var msg = { message: [client.sessionId, message] };    
		//client.broadcast(msg);
	  }) 
	  client.on('disconnect', function(){ 
		//client.broadcast({ announcement: client.sessionId + ' disconnected'  });
	  }) 
  }); 

  queue.subscribe(function(message){
    //console.log("received message");
	//console.log(message.data.toString());
	socket.broadcast({message: message.data.toString()});    
    //console.log("===========================")    
  });

});  








