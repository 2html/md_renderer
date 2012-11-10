## AUTHOR: Tom Tang (tly1980@gmail.com)
## License:  MIT

##############################################################
##  SIMPLE TEST                                             ##
##  cd md_renderer/webserver                                ##
##  1. python app.py                                        ##
##  2. python worker_mockup.py                              ##
##  3. http -f POST localhost:8888/md md_src="hello word"   ##
##                                                          ##
##  p.s.: step3 require httpie, or you could use curl       ##
###############################################################

import tornado.ioloop
import tornado.web
from tornado.web import asynchronous
from tornado import gen
from settings import SERVER_IP, SERVER_PORT, BIND_ADDR, DIST_PORT, RESULT_PORT
from zmq.eventloop import ioloop
from uuid import uuid4 as uuid
import zmq
from zmq.eventloop.zmqstream import ZMQStream
import simplejson as json

# This line are require to call before the tornado IOLoop being start
# Explanation: http://zeromq.github.com/pyzmq/eventloop.html
ioloop.install()

# init zmq context
context = zmq.Context()
#  Socket to talk to server
# This web server would have both:
# push (task distribution) and       -- MAP
# pull (task result collection)      -- REDUCE
socket_push = context.socket(zmq.PUSH)
socket_push.bind(BIND_ADDR + ':' + DIST_PORT)
socket_pull = context.socket(zmq.PULL)
socket_pull.bind(BIND_ADDR + ':' + RESULT_PORT)


zstream_push = ZMQStream(socket_push)
zstream_pull = ZMQStream(socket_pull)

# global dictionary variable to collect the result
result_dict = {}


############
##  PULL  ##
############

def update_result(msg_list):
# function to collect the result
    for msg in msg_list:
        m = json.loads(msg)
        result_dict[m['uuid']] = m
zstream_pull.on_recv(update_result)


class MDHandler(tornado.web.RequestHandler):
    reult = None

    @asynchronous
    @gen.engine
    def post(self):
        self.result_key = str(uuid())
        self.result = None

        md_src = self.get_argument('md_src', None)
        msg = {
            'uuid': self.result_key,
            'md_src': md_src
        }

        ############
        ##  PUSH  ##
        ############
        # task format: {'uuid','md_src'}
        # push the task in ASYN-Fashion.
        # P.S. zstream send method provide the callback function already.
        # So it would work properly with gen.Task.
        yield gen.Task(zstream_push.send_unicode,
            json.dumps(msg))

        #######################
        ##  Pending on PULL  ##
        #######################
        # result format: {'uuid','md_src', 'html'}
        while not self.result:
            # keep checking in ASYN-Fashion
            yield gen.Task(self.check_result)

        self.write(self.result['html'])
        self.finish()

    # callback parameter is essential,
    # as the make gen.Task work properly
    def check_result(self, callback=None):
        self.result = result_dict.get(self.result_key)
        tornado.ioloop.IOLoop.instance().add_callback(callback)

application = tornado.web.Application([
    (r"/md", MDHandler),
])

if __name__ == "__main__":
    application.listen(SERVER_PORT, SERVER_IP)

    tornado.ioloop.IOLoop.instance().start()
