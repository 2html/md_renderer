"use strict"
request = require 'request'
dispatcher = require '..'
exec = require('child_process').exec
assert = require 'assert'

renderer = undefined



console.log('starting render')
renderer = exec('bundle exec ruby render_worker.rb', 
    {
        cwd: '../../renderer/'
    },(err, stdout, stderr)->
     console.log('some error happened on starting render', err) if err
)

port = 3001
setInterval(
    ()->
        dispatcher.app.listen port, ()->
            r2 = request.post({
                    url:'http://localhost:' + port + '/md', 
                    form: {src: "*hello world*"}
                } , 
                (e, r, body)->
                    console.log('body:', body, k)
                    k = renderer.kill()
                    assert.equal body, '<p><em>hello world</em></p>\n'
                    process.exit(0)
            )
    ,
    1000
)

