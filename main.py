try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from httpserver import HTTPServer

server = HTTPServer("127.0.0.1", 8000)


@server.route("/")
def get_index(request):
    return 200, {}, b"""<h1>Hello World!</h>
<form action='/' method='POST'>
    <input name='name' placeholder='enter name here...'>
    <button>Submit</button>
</form>"""


@server.route("/", "POST")
def post_name(request):
    form = request.form
    return 200, {}, f"<h1>Hello {form['name']}!</h1>".encode()


loop = asyncio.new_event_loop()
try:
    loop.run_until_complete(server.start())
    loop.run_forever()
except KeyboardInterrupt:
    server._server.close()
finally:
    loop.close()
