# Quick-Start
## Minimal App

```python
import asyncio

from httpserver import HTTPServer
from httpserver.constants import STATUS_OK_200

app = HTTPServer()


@app.route("/")
def get_index(context):
    return context.response.html(STATUS_OK_200, "<h1>Hello World!</h1>")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(app.start("0.0.0.0", 80))
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(app.stop())
    finally:
        loop.close()
```
