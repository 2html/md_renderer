(function() {
  "use strict";

  var assert, dispatcher, exec, port, renderer, request;

  request = require('request');

  dispatcher = require('..');

  exec = require('child_process').exec;

  assert = require('assert');

  renderer = void 0;

  console.log('starting render');

  renderer = exec('bundle exec ruby render_worker.rb', {
    cwd: '../../renderer/'
  }, function(err, stdout, stderr) {
    if (err) {
      return console.log('some error happened on starting render', err);
    }
  });

  port = 3001;

  setInterval(function() {
    return dispatcher.app.listen(port, function() {
      var r2;
      return r2 = request.post({
        url: 'http://localhost:' + port + '/md',
        form: {
          src: "*hello world*"
        }
      }, function(e, r, body) {
        var k;
        console.log('body:', body, k);
        k = renderer.kill();
        assert.equal(body, '<p><em>hello world</em></p>\n');
        return process.exit(0);
      });
    });
  }, 1000);

}).call(this);
