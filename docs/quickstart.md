# Quick-Start
## Minimal App

```python
import asyncio

from httpserver import HTTPServer

app = HTTPServer("0.0.0.0", 80)


@app.route("/")
def get_index(context):
    return context.response.html(200, "<h1>Hello World!</h1>")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(app.start())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        app._server.close()
        loop.close()
```
