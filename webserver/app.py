"""
AUTHOR: Tom Tang (tly1980@gmail.com)
License:  MIT


SIMPLE TEST
1. cd md_renderer/webserver
   python app.py
2. cd md_renderer/renderer
   bundle exec ruby render_worker.py
3. http -f POST localhost:8888/md src="hello word"

p.s.: 'http' is the command of httpie (https://github.com/jkbr/httpie), 
or you could use curl.
"""

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


def update_result(msg_list):
    """
    for collecting the result
    msg_list - the list containing the result.

    PS: loop is necessary, as it may get more than one result.
    """
    for msg in msg_list:
        m = json.loads(msg)
        result_dict[m['uuid']] = m

# registering the callback
zstream_pull.on_recv(update_result)


class MDHandler(tornado.web.RequestHandler):
    reult = None

    @asynchronous
    @gen.engine
    def post(self):
        # key for this task
        self.result_key = str(uuid())
        self.result = None

        # pack the task
        src = self.get_argument('src', None)
        msg = {
            'uuid': self.result_key,
            'src': src
        }

        """
        Step1. PUSH
        ===========
        task format: {'uuid','src'}
        push the task in ASYN-Fashion.
        P.S. zstream send method provide the callback function already.
        So it would work properly with gen.Task.
        """
        yield gen.Task(zstream_push.send_unicode,
            json.dumps(msg))

        """
        Step2. Waiting the result
        ======================
        result format: {'uuid','src', 'html'}
        keep checking in ASYN-Fashion

        Considering moving this bit to a global PeriodicCallback.
        So it does adding new check_result as a ioloop callback
        for every request comes in.
        """
        while not self.result:
            yield gen.Task(self.check_result)

        """
        Step3. Return the rendered result.
        """
        self.write(self.result['html'])
        self.finish()

    def check_result(self, callback=None):
        """
        callback parameter is essential,
        as the make gen.Task work properly
        """
        self.result = result_dict.get(self.result_key)
        tornado.ioloop.IOLoop.instance().add_callback(callback)

application = tornado.web.Application([
    (r"/md", MDHandler),
])

if __name__ == "__main__":
    application.listen(SERVER_PORT, SERVER_IP)
    tornado.ioloop.IOLoop.instance().start()
