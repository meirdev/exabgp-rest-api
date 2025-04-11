import asyncio
import random

import httpx
import pytest


def _random_ip() -> str:
    return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"


@pytest.mark.asyncio
async def test_concurrent_requests():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:5000/neighbors",
            json={
                "ip_address": "127.0.0.1",
                "router_id": "1.1.1.1",
                "local_address": "127.0.0.1",
                "local_as": 65001,
                "peer_as": 65010,
                "connect": 1000,
                "capability": {"route_refresh": True},
            },
        )
        assert response.is_success

    async def inner():
        async with httpx.AsyncClient() as client:
            for _ in range(100):
                action = random.choice(["announce", "withdraw"])

                response = await client.post(
                    f"http://127.0.0.1:5000/neighbors/127.0.0.1/flows/{action}",
                    json={
                        "match": {
                            "destination": "10.0.0.0/24",
                            "source": _random_ip(),
                            "port": random.randint(1, 65535),
                            "protocol": random.choice(["tcp", "udp", "icmp"]),
                            "packet_length": random.randint(1, 1500),
                        },
                        "then": "discard",
                    },
                )

                assert response.status_code == 200

    await asyncio.gather(*[inner() for _ in range(10)])
