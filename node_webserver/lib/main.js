(function() {
  "use strict";

  var d;

  d = require('..');

  d.server.listen(3000, function() {
    return console.log('Server is running on: ', d.server.address());
  });

}).call(this);
