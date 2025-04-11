from typing import Literal

from pydantic import BaseModel, IPvAnyAddress, IPvAnyNetwork, conint

type Port = conint(ge=0, le=65535)  # type: ignore

type Protocol = Literal[
    "icmp",
    "igmp",
    "tcp",
    "egp",
    "udp",
    "rsvp",
    "gre",
    "esp",
    "ah",
    "ospf",
    "ipip",
    "pim",
    "sctp",
]

type TcpFlag = Literal[
    "fin",
    "syn",
    "rst",
    "push",
    "ack",
    "urg",
    "ece",
    "cwr",
    "ns",
]

type IcmpCode = Literal[
    "network-unreachable",
    "host-unreachable",
    "protocol-unreachable",
    "port-unreachable",
    "fragmentation-needed",
    "source-route-failed",
    "destination-network-unknown",
    "destination-host-unknown",
    "source-host-isolated",
    "destination-network-prohibited",
    "destination-host-prohibited",
    "network-unreachable-for-tos",
    "host-unreachable-for-tos",
    "communication-prohibited-by-filtering",
    "host-precedence-violation",
    "precedence-cutoff-in-effect",
    "redirect-for-network",
    "redirect-for-host",
    "redirect-for-tos-and-net",
    "redirect-for-tos-and-host",
    "ttl-eq-zero-during-transit",
    "ttl-eq-zero-during-reassembly",
    "required-option-missing",
    "ip-header-bad",
]

type IcmpType = Literal[
    "echo-reply",
    "unreachable",
    "redirect",
    "echo-request",
    "router-advertisement",
    "router-solicit",
    "time-exceeded",
    "parameter-problem",
    "timestamp",
    "timestamp-reply",
    "photuris",
    "experimental-mobility",
    "extended-echo-request",
    "extended-echo-reply",
    "experimental-one",
    "experimental-two",
]

type Fragment = Literal[
    "dont-fragment",
    "is-fragment",
    "first-fragment",
    "last-fragment",
]

type Action = Literal[
    "accept",
    "discard",
    "rate-limit",
]

type AnyStr[T] = T | str

type Community = tuple[int, int]


class NeighborCapability(BaseModel):
    route_refresh: bool = True


class Neighbor(BaseModel):
    ip_address: IPvAnyAddress
    description: str | None = None
    router_id: IPvAnyAddress | None = None
    local_address: IPvAnyAddress | None = None
    local_as: int | None = None
    peer_as: int | None = None
    connect: int | None = None
    capability: NeighborCapability | None = None


class FlowMatch(BaseModel):
    source: IPvAnyNetwork | None = None
    destination: IPvAnyNetwork | None = None
    port: AnyStr[Port] | None = None
    source_port: AnyStr[Port] | None = None
    destination_port: AnyStr[Port] | None = None
    protocol: AnyStr[Protocol] | None = None
    tcp_flags: AnyStr[TcpFlag] | None = None
    icmp_type: AnyStr[IcmpType] | None = None
    icmp_code: AnyStr[IcmpCode] | None = None
    fragment: AnyStr[Fragment] | None = None
    packet_length: AnyStr[int] | None = None


class FlowRateLimit(BaseModel):
    rate_limit: int


class Flow(BaseModel):
    match: FlowMatch
    then: Literal["accept", "discard"] | FlowRateLimit


class Route(BaseModel):
    prefix: IPvAnyNetwork
    next_hop: IPvAnyAddress | None = None
    community: list[Community] | None = None
