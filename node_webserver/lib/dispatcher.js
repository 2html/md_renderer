(function() {
  "use strict";

  var ADDR, RESULT_PORT, TASK_PORT, app, express, http, results, server, sock_pull, sock_push, uuid, zmq;

  express = require('express');

  zmq = require('zmq');

  uuid = require('node-uuid');

  http = require('http');

  ADDR = 'tcp://127.0.0.1';

  TASK_PORT = '5555';

  RESULT_PORT = '5556';

  sock_push = zmq.socket('push');

  sock_pull = zmq.socket('pull');

  sock_push.bind(ADDR + ':' + TASK_PORT);

  sock_pull.bind(ADDR + ':' + RESULT_PORT);

  app = express();

  app.use(express.bodyParser());

  server = http.createServer(app);

  results = {};

  sock_pull.on('message', function(msg) {
    var msg_obj, r;
    console.log('on msg');
    msg_obj = JSON.parse(msg);
    console.log('msg', msg_obj);
    r = results[msg_obj.id];
    r.res.end(msg_obj.html);
    return delete results[msg_obj.id];
  });

  app.post('/md', function(req, res) {
    var id, msg, src;
    id = uuid.v4();
    src = req.body.src;
    results[id] = {
      id: id,
      res: res,
      src: src
    };
    console.log('req.params', req.body.src, req.url);
    msg = JSON.stringify({
      id: id,
      src: src
    });
    sock_push.send(msg);
    return console.log('after send');
  });

  app.get('/', function(req, res) {
    return res.send("2html render");
  });

  exports.app = app;

  exports.server = server;

  exports.results = results;

}).call(this);
