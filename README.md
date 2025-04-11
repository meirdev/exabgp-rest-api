# ExaBGP REST API

This is a simple REST API for ExaBGP. It allows you to interact with ExaBGP using HTTP requests.

## Usage

Use `docker-compose` to start the ExaBGP container and the REST API container.

```bash
docker-compose up -d
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
