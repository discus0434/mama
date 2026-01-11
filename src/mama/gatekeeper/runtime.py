import uvicorn
from fastapi import FastAPI

from mama.env import load_config_from_env
from mama.gatekeeper.app import create_app


def build_app() -> FastAPI:
    config = load_config_from_env()
    return create_app(config)


def run() -> None:
    config = load_config_from_env()
    uvicorn.run(
        create_app(config),
        host=config.gatekeeper.host,
        port=config.gatekeeper.port,
    )


app = build_app()

if __name__ == "__main__":
    run()
