#!/usr/bin/env python3

import argparse
import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator

import uvicorn
from fastapi import Body, FastAPI, HTTPException, Response, status
from fastapi.responses import JSONResponse
from pydantic import IPvAnyAddress

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.dto import Flow, Neighbor, Route
from app.utils import (
    flow_to_command,
    route_to_command,
    send_command,
    update_config,
)

DEFUALT_HOST = os.getenv("HOST", "0.0.0.0")

DEFAULT_PORT = os.getenv("PORT", 5000)

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
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    logger.info("Hello")

    yield


async def command_executor(command: str) -> JSONResponse:
    logger.info("Executing command: %s", command)

    response = await send_command(command)

    logger.info("Command response: %s", response)

    if response == "error":
        logger.error("Failed to execute command: %s", command)

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "message": "Failed to execute command",
                "command": command,
            },
        )

    logger.info("Command executed successfully: %s", command)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "success", "command": command, "response": response},
    )


app = FastAPI(lifespan=lifespan)


@app.post("/command")
async def write_command(command: str = Body(...)):
    return await command_executor(command)


@app.post("/neighbors")
async def add_or_update_neighbor(neighbor: Neighbor, response: Response):
    exists = update_config(CONFIG_PATH, neighbor.ip_address, neighbor)

    if not exists:
        logger.info("Neighbor %s added", neighbor)

        response.status_code = status.HTTP_201_CREATED
    else:
        logger.info("Neighbor %s updated", neighbor)

        response.status_code = status.HTTP_200_OK

    return await command_executor("reload")


@app.delete("/neighbors/{neighbor}")
async def delete_neighbor(neighbor: IPvAnyAddress):
    exists = update_config(CONFIG_PATH, neighbor, None)

    if not exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    logger.info("Neighbor %s deleted", neighbor)

    return await command_executor("reload")


@app.post("/neighbors/{neighbor}/routes/announce")
async def announce_route(neighbor: IPvAnyAddress, route: Route):
    command = route_to_command(neighbor, "announce", route)

    return await command_executor(command)


@app.post("/neighbors/{neighbor}/routes/withdraw")
async def withdraw_route(neighbor: IPvAnyAddress, route: Route):
    command = route_to_command(neighbor, "withdraw", route)

    return await command_executor(command)


@app.post("/neighbors/{neighbor}/flows/announce")
async def announce_flow(neighbor: IPvAnyAddress, flow: Flow):
    command = flow_to_command(neighbor, "announce", flow)

    return await command_executor(command)


@app.post("/neighbors/{neighbor}/flows/withdraw")
async def withdraw_flow(neighbor: IPvAnyAddress, flow: Flow):
    command = flow_to_command(neighbor, "withdraw", flow)

    return await command_executor(command)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="ExaBGP API")
    arg_parser.add_argument(
        "--host",
        type=str,
        default=DEFUALT_HOST,
        help="Host to bind the server to",
    )
    arg_parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="Port to bind the server to",
    )

    args = arg_parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port, log_config=LOG_CONFIG)
