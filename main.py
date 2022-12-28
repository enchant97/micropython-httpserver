try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from httpserver import HTTPServer

server = HTTPServer("127.0.0.1", 8000)


@server.route("/")
def get_index(context):
    return context.response.html(200, """<h1>Hello World!</h>
<form action='/' method='POST'>
    <input name='name' placeholder='enter name here...'>
    <button>Submit</button>
</form>""")


@server.route("/", "POST")
def post_name(context):
    form = context.request.form
    return context.response.html(200, f"<h1>Hello {form['name']}!</h1>")


loop = asyncio.new_event_loop()
try:
    loop.run_until_complete(server.start())
    loop.run_forever()
except KeyboardInterrupt:
    server._server.close()
finally:
    loop.close()
