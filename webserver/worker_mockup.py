import zmq
from settings import RESULT_PORT, DIST_PORT, CONN_ADDR


context = zmq.Context()
socket_pull = context.socket(zmq.PULL)
socket_pull.connect(CONN_ADDR + ':' + DIST_PORT)

socket_pub = context.socket(zmq.PUB)
socket_pub.connect(CONN_ADDR + ':' + RESULT_PORT)

while True:
    #  Wait for next request from client
    message = socket_pull.recv()
    print "Received request: ", message
    socket_pub.send(message)
