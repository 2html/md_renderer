"use strict"
describe "md dispatcher", ()->
    request = require 'request'
    dispatcher = require '..'
    exec = require('child_process').exec
    assert = require 'assert'
    path = require 'path'
    zmq = require 'zmq'

    renderer = undefined
    render_folder = path.resolve(__dirname, '../../renderer/')
    cmd = 'bundle exec ruby render_worker.rb'

    inbound_ready = zmq.socket('pull')
    inbound_ready.bind('tcp://127.0.0.1:5557')
    ready_done = null

    inbound_ready.on 'message', (msg) ->
        console.log('msg', msg)
        ready_done()

    console.log 'starting render @:', render_folder, 'cmd:', cmd
    renderer = exec(cmd,  {cwd: render_folder}, (err, stdout, stderr)->
            console.log('some error happened on starting render', err) if err
    )

    before (done)->
        ready_done = done
        #setTimeout(done, 500)

    after (done)->
        renderer.kill('SIGKILL') if renderer
        done()


    port = 0
    it 'should return the render result correctly', (done)->
        dispatcher.server.listen port, ()->
            console.log "opened server on %j", dispatcher.server.address().port
            r2 = request.post({
                    url:'http://localhost:' + dispatcher.server.address().port + '/md', 
                    form: {src: "*hello world*"}
                } , 
                (e, r, body)->
                    #console.log('body:', body)
                    assert.equal body, '<p><em>hello world</em></p>\n'
                    done()
            )

