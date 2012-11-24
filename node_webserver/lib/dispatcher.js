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

  sock_push.bindSync(ADDR + ':' + TASK_PORT);

  sock_pull.bindSync(ADDR + ':' + RESULT_PORT);

  app = express();

  app.use(express.bodyParser());

  server = http.createServer(app);

  results = {};

  sock_pull.on('message', function(msg) {
    var msg_obj, r, res;
    msg_obj = JSON.parse(msg);
    console.log('msg', msg_obj);
    r = results[msg_obj.id];
    res = r.res;
    console.log('before res.finished', res.finished);
    r.res.end(msg_obj.html);
    console.log('preparing to delete', msg_obj.id);
    console.log('after res.finished', res.finished);
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
    msg = JSON.stringify({
      id: id,
      src: src
    });
    sock_push.send(msg);
    return console.log('res.finished', res.finished);
  });

  app.get('/', function(req, res) {
    return res.send("2html render");
  });

  exports.app = app;

  exports.server = server;

  exports.results = results;

}).call(this);
