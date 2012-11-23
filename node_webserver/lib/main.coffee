"use strict"
d = require '..'

d.server.listen 3000, ()->
	console.log('on callback')