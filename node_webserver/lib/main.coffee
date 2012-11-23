"use strict"
d = require '..'

d.app.listen 3000, ()->
	console.log('on callback')