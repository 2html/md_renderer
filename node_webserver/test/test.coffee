"use strict"
describe "md dispatcher", ()->
    request = require 'request'
    dispatcher = require '..'
    exec = require('child_process').exec
    assert = require 'assert'
    path = require 'path'
    renderer = undefined
    render_folder = path.resolve(__dirname, '../../renderer/')

    before (done)->
        console.log 'starting render @:', render_folder
        renderer = exec('bundle exec ruby render_worker.rb', 
            {
                cwd: render_folder
            },

            (err, stdout, stderr)->
                console.log('some error happened on starting render', err) if err
                done()

        )

        


    after (done)->
        renderer.kill() if renderer
        setTimeout(done, 500)


    port = 0
    a = 0
    it 'should return the render result correctly', (done)->
        dispatcher.server.listen port, ()->
            a+=1
            console.log "opened server on %j", dispatcher.server.address().port, 'a', a
            r2 = request.post({
                    url:'http://localhost:' + dispatcher.server.address().port + '/md', 
                    form: {src: "*hello world*"}
                } , 
                (e, r, body)->
                    console.log('body:', body, k)
                    assert.equal body, '<p><em>hello world</em></p>\n'
                    done()
            )

