(function() {
  "use strict";

  var d;

  d = require('..');

  d.app.listen(3000, function() {
    return console.log('on callback');
  });

}).call(this);
