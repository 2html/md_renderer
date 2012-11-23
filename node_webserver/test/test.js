(function() {
  "use strict";

  describe("md dispatcher", function() {
    var assert, cmd, dispatcher, exec, inbound_ready, path, port, ready_done, render_folder, renderer, request, zmq;
    request = require('request');
    dispatcher = require('..');
    exec = require('child_process').exec;
    assert = require('assert');
    path = require('path');
    zmq = require('zmq');
    renderer = void 0;
    render_folder = path.resolve(__dirname, '../../renderer/');
    cmd = 'bundle exec ruby render_worker.rb';
    inbound_ready = zmq.socket('pull');
    inbound_ready.bind('tcp://127.0.0.1:5557');
    ready_done = null;
    inbound_ready.on('message', function(msg) {
      console.log('msg', msg);
      return ready_done();
    });
    console.log('starting render @:', render_folder, 'cmd:', cmd);
    renderer = exec(cmd, {
      cwd: render_folder
    }, function(err, stdout, stderr) {
      if (err) {
        return console.log('some error happened on starting render', err);
      }
    });
    before(function(done) {
      return ready_done = done;
    });
    after(function(done) {
      if (renderer) {
        renderer.kill('SIGKILL');
      }
      return done();
    });
    port = 0;
    return it('should return the render result correctly', function(done) {
      return dispatcher.server.listen(port, function() {
        var r2;
        console.log("opened server on %j", dispatcher.server.address().port);
        return r2 = request.post({
          url: 'http://localhost:' + dispatcher.server.address().port + '/md',
          form: {
            src: "*hello world*"
          }
        }, function(e, r, body) {
          assert.equal(body, '<p><em>hello world</em></p>\n');
          return done();
        });
      });
    });
  });

}).call(this);
