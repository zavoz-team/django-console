import uvicorn

from adapter.config.loader import load_config
from adapter.http.fastapi.app import create_app

config = load_config()
app = create_app(config)


def run() -> None:
    uvicorn.run(app, host=config.http.host, port=config.http.port)


if __name__ == '__main__':
    run()
