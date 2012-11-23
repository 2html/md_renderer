"use strict"
d = require '..'

d.server.listen 3000, ()->
	console.log 'Server is running on: ', d.server.address() 