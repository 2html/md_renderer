require 'redcarpet'
require 'zmq'
require 'json'

context = ZMQ::Context.new(1)

puts "Opening connection pulling task"
inbound = context.socket(ZMQ::PULL)
inbound.connect("tcp://127.0.0.1:5555")

puts "Opening connection pushing result"
outbound = context.socket(ZMQ::PUSH)
outbound.connect("tcp://127.0.0.1:5556")

outbound_ready = context.socket(ZMQ::PUSH)
outbound_ready.connect("tcp://127.0.0.1:5557")


markdown = Redcarpet::Markdown.new(Redcarpet::Render::HTML,
        :autolink => true, :space_after_headers => true)

markdown.render("This is *bongos*, indeed.")
outbound_ready.send('ready')
loop do
  msg = inbound.recv
  task = JSON(msg)
  task['html'] = markdown.render task['src']
  task['renderer'] = 'Redcarpet:' + Redcarpet::VERSION
  outbound.send JSON(task)
  puts 'rendered: ' + task['html']
end

