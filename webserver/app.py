import tornado.ioloop
import tornado.web
from tornado.web import asynchronous
from tornado import gen
from settings import SERVER_IP, SERVER_PORT, BIND_ADDR, CONN_ADDR, DIST_PORT, RESULT_PORT
from zmq.eventloop import ioloop
from uuid import uuid4 as uuid
ioloop.install()


import zmq
from zmq.eventloop.zmqstream import ZMQStream
import simplejson as json


context = zmq.Context()

#  Socket to talk to server
print "Connecting to hello world server..."
socket_push = context.socket(zmq.PUSH)
socket_push.bind(BIND_ADDR + ':' + DIST_PORT)
socket_pull = context.socket(zmq.PULL)
socket_pull.bind(BIND_ADDR + ':' + RESULT_PORT)


zstream_push = ZMQStream(socket_push)
zstream_pull = ZMQStream(socket_pull)

result_dict = {}


def update_result(msg):
    ret = json.loads(msg[0])
    result_dict[ret['uuid']] = ret

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

        yield gen.Task(zstream_push.send_unicode,
            json.dumps(msg))

        while not self.result:
            yield gen.Task(self.check_result)

        self.write(json.dumps(self.result))
        self.finish()

    def check_result(self, callback=None):
        self.result = result_dict.get(self.result_key)
        tornado.ioloop.IOLoop.instance().add_callback(callback)

application = tornado.web.Application([
    (r"/md", MDHandler),
])

if __name__ == "__main__":
    application.listen(SERVER_PORT, SERVER_IP)

    tornado.ioloop.IOLoop.instance().start()
