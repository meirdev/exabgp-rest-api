# ExaBGP REST API

[![Docker Image CI](https://github.com/meirdev/exabgp-rest-api/actions/workflows/docker-image.yml/badge.svg)](https://github.com/meirdev/exabgp-rest-api/actions/workflows/docker-image.yml)

This is a simple REST API for ExaBGP, it allows you to interact with ExaBGP using HTTP requests.

## Usage

Use the following command to run the ExaBGP REST API:

```bash
docker run -d -p 5000:5000 -p 179:179 --name exabgp-rest-api meirdev/exabgp-rest-api
```

Note: If you want to save the configuration files, you can mount a volume to the container. For example:

```bash
docker run -d -p 5000:5000 -p 179:179 --name exabgp-rest-api -v /path/to/config:/etc/exabgp meirdev/exabgp-rest-api
```

## Endpoints

`POST /neighbors`

Add a new neighbor.

```bash
curl --location 'http://127.0.0.1:5000/neighbors' \
--header 'Content-Type: application/json' \
--data '{"ip_address": "127.0.0.1", "router_id": "1.1.1.1", "local_address": "127.0.0.1", "local_as": 65001, "peer_as": 65010, "connect": 1000, "capability":{"route_refresh": true}}'
```

`DELETE /neighbors/{ip_address}`

Delete a neighbor.

```bash
curl --location --request DELETE 'http://127.0.0.1:5000/neighbors/127.0.0.1'
```

`POST /neighbors/{ip_address}/flows/announce`

Announce a flow to a neighbor.

```bash
curl --location 'http://127.0.0.1:5000/neighbors/127.0.0.1/flows/announce' \
--header 'Content-Type: application/json' \
--data '{"match": {"destination": "10.0.0.0/24", "port": "http"}, "then": "discard"}'
```

`POST /neighbors/{ip_address}/flows/withdraw`

Withdraw a flow from a neighbor.

```bash
curl --location 'http://127.0.0.1:5000/neighbors/127.0.0.1/flows/withdraw' \
--header 'Content-Type: application/json' \
--data '{"match": {"destination": "10.0.0.0/24", "port": "http"}, "then": "discard"}'
```

`POST /neighbors/{ip_address}/routes/announce`

Announce a route to a neighbor.

```bash
curl --location 'http://127.0.0.1:5000/neighbors/127.0.0.1/routes/announce' \
--header 'Content-Type: application/json' \
--data '{"prefix": "10.0.0.0/24", "next_hop": "255.255.255.255", "community": [[64500, 666]]}'
```

`POST /neighbors/{ip_address}/routes/withdraw`

Withdraw a route from a neighbor.

```bash
curl --location 'http://127.0.0.1:5000/neighbors/127.0.0.1/routes/withdraw' \
--header 'Content-Type: application/json' \
--data '{"prefix": "10.0.0.0/24", "next_hop": "255.255.255.255", "community": [[64500, 666]]}'
```
