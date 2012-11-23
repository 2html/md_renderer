(function() {
  "use strict";

  describe("md dispatcher", function() {
    var a, assert, dispatcher, exec, path, port, render_folder, renderer, request;
    request = require('request');
    dispatcher = require('..');
    exec = require('child_process').exec;
    assert = require('assert');
    path = require('path');
    renderer = void 0;
    render_folder = path.resolve(__dirname, '../../renderer/');
    before(function(done) {
      console.log('starting render @:', render_folder);
      return renderer = exec('bundle exec ruby render_worker.rb', {
        cwd: render_folder
      }, function(err, stdout, stderr) {
        if (err) {
          console.log('some error happened on starting render', err);
        }
        return done();
      });
    });
    after(function(done) {
      if (renderer) {
        renderer.kill();
      }
      return setTimeout(done, 500);
    });
    port = 0;
    a = 0;
    return it('should return the render result correctly', function(done) {
      return dispatcher.server.listen(port, function() {
        var r2;
        a += 1;
        console.log("opened server on %j", dispatcher.server.address().port, 'a', a);
        return r2 = request.post({
          url: 'http://localhost:' + dispatcher.server.address().port + '/md',
          form: {
            src: "*hello world*"
          }
        }, function(e, r, body) {
          console.log('body:', body, k);
          assert.equal(body, '<p><em>hello world</em></p>\n');
          return done();
        });
      });
    });
  });

}).call(this);
