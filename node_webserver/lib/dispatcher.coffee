"use strict"

express = require 'express'
zmq = require 'zmq'
uuid = require 'node-uuid'

ADDR = 'tcp://127.0.0.1'
TASK_PORT = '5555'
RESULT_PORT = '5556'


sock_push = zmq.socket('push')
sock_pull = zmq.socket('pull')

sock_push.bind(ADDR + ':' + TASK_PORT)
sock_pull.bind(ADDR + ':' + RESULT_PORT)

app = express()
app.use(express.bodyParser())

results = {}

sock_pull.on('message', (msg) ->
    console.log('on msg')
    msg_obj = JSON.parse(msg)
    console.log('msg', msg_obj)
    r = results[msg_obj.id]
    r.res.end(msg_obj.html)
    delete results[msg_obj.id]
);

app.post('/md',
    (req, res)->
        id = uuid.v4()
        src = req.body.src
        results[id] = {id: id, res: res, src: src}
        console.log('req.params', req.body.src, req.url)
        msg = JSON.stringify({id:id, src:src})
        sock_push.send(msg)
        console.log('after send')
)

app.get('/', 
    (req, res)->
        res.send "2html render"
)
 
exports.app = app
exports.results = results
#app.listen 3000

#console.log('export' , exports)
#console.log('require.main' , require.main)
