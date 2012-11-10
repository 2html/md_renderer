import zmq
from settings import RESULT_PORT, DIST_PORT, CONN_ADDR
import simplejson as json

context = zmq.Context()
socket_pull = context.socket(zmq.PULL)
socket_pull.connect(CONN_ADDR + ':' + DIST_PORT)

socket_pub = context.socket(zmq.PUB)
socket_pub.connect(CONN_ADDR + ':' + RESULT_PORT)

while True:
    #  Wait for next request from client
    message = json.loads(socket_pull.recv())
    # this is a mockup, just to provide a fake html retun
    message['html'] = message['src']
    message['renderer'] = 'echo mockup'
    print "message being send:", message
    socket_pub.send(json.dumps(message))
