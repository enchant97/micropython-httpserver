try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from httpserver import HTTPServer

server = HTTPServer("127.0.0.1", 8000)
loop = asyncio.new_event_loop()
try:
    loop.run_until_complete(server.start())
    loop.run_forever()
except KeyboardInterrupt:
    server._server.close()
finally:
    loop.close()
