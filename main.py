import asyncio
from time import sleep

from httpserver import HTTPServer

server = HTTPServer("127.0.0.1", 8000, globals={
    "message": "Hello World!",
})


@server.route("/")
def get_index(ctx):
    message = ctx.globals["message"]
    return ctx.response.html(200, f"""<h1>{message}</h>
<form action='/' method='POST'>
    <input name='name' placeholder='enter name here...'>
    <button>Submit</button>
</form>""")


@server.route("/stream")
def get_stream(ctx):
    def my_stream():
        for i in range(100):
            yield "Hello '{0}'\n".format(i).encode()
            sleep(.01)
    return ctx.response.content_stream(200, "text/plain", my_stream())


@server.route("/LICENSE.txt")
def get_file(ctx):
    return ctx.response.file("LICENSE.txt")


@server.route("/", "POST")
def post_name(ctx):
    form = ctx.request.form()
    return ctx.response.html(200, f"<h1>Hello {form['name']}!</h1>")


@server.route("/api")
def get_api_index(ctx):
    return ctx.response.json(200, {"message": "Hello World!"})


@server.route("/api", "POST")
def post_api_name(ctx):
    form = ctx.request.json()
    return ctx.response.json(200, {"message": f"Hello {form['name']}!"})


loop = asyncio.new_event_loop()
try:
    loop.run_until_complete(server.start())
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(server.stop())
finally:
    loop.close()
