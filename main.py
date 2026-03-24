import uvicorn

from adapter.http.django.asgi import application
from adapter.http.django.runtime import get_config

config = get_config()


def run() -> None:
    uvicorn.run(application, host=config.http.host, port=config.http.port)


if __name__ == '__main__':
    run()
