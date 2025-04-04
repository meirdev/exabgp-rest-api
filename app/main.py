#!/usr/bin/env python3

import argparse
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator

import uvicorn
from fastapi import Body, FastAPI, HTTPException, Response, status
from pydantic import IPvAnyAddress

from app.dto import Flow, Neighbor, Route
from app.utils import (
    flow_to_command,
    reload,
    route_to_command,
    send_command,
    update_config,
)

CONFIG_PATH = Path("/etc/exabgp/exabgp.conf")

# We need to send all logs to stderr, because exabgp uses stdout as input
LOG_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "stream": sys.stderr,
        },
    },
}

logger = logging.getLogger("exabgp-api")
logger.setLevel(logging.DEBUG)

logger_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger_handler = logging.StreamHandler(sys.stderr)
logger_handler.setFormatter(logger_formatter)
logger.addHandler(logger_handler)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    logger.info("Hello")

    yield


app = FastAPI(root_path="/bgp", lifespan=lifespan)


@app.post("/command")
async def write_command(command: str = Body(...)):
    if not await send_command(command):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@app.post("/neighbors")
async def add_or_update_neighbor(neighbor: Neighbor, response: Response):
    exists = update_config(CONFIG_PATH, neighbor.ip_address, neighbor)

    if not exists:
        logger.info("Neighbor %s added", neighbor)

        response.status_code = status.HTTP_201_CREATED
    else:
        logger.info("Neighbor %s updated", neighbor)

        response.status_code = status.HTTP_200_OK

    reload()


@app.delete("/neighbors/{neighbor}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_neighbor(neighbor: IPvAnyAddress):
    exists = update_config(CONFIG_PATH, neighbor, None)

    if not exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    logger.info("Neighbor %s deleted", neighbor)

    reload()


@app.post("/neighbors/{neighbor}/routes", status_code=status.HTTP_200_OK)
async def add_route(neighbor: IPvAnyAddress, route: Route):
    command = route_to_command(neighbor, "announce", route)

    if not await send_command(command):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@app.delete("/neighbors/{neighbor}/routes", status_code=status.HTTP_200_OK)
async def delete_route(neighbor: IPvAnyAddress, route: Route):
    command = route_to_command(neighbor, "withdraw", route)

    if not await send_command(command):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@app.post("/neighbors/{neighbor}/flows", status_code=status.HTTP_204_NO_CONTENT)
async def add_flow(neighbor: IPvAnyAddress, flow: Flow):
    command = flow_to_command(neighbor, "announce", flow)

    if not await send_command(command):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


@app.delete("/neighbors/{neighbor}/flows", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flow(neighbor: IPvAnyAddress, flow: Flow):
    command = flow_to_command(neighbor, "withdraw", flow)

    if not await send_command(command):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="ExaBGP API")
    arg_parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the server to",
    )
    arg_parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to bind the server to",
    )

    args = arg_parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port, log_config=LOG_CONFIG)
