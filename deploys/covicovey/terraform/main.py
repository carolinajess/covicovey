"""Serve cov.ing/covey as Cloudflare Workers Assets.

cov.ing is shared: mublog owns the zone root, its route, and the append-slash ruleset.
"""

from os import environ

from helicopyter import Block, registry, resource
from helicopyter.cloudflare import jam
from stacks.base import provide

provide('cloudflare/cloudflare', '5.25.0')

# Foundational networking for cov.ing
# Main, and use-jam until main first deploys, owns the proxied wildcard previews require
resource.cloudflare_dns_record.this(
    content='100::',
    count=Block('contains(["main", "use-jam"], terraform.workspace) ? 1 : 0'),
    name='*.cov.ing',
    proxied=True,
    ttl=1,
    type='AAAA',
    zone_id=environ['CLOUDFLARE_ZONE_ID'],
)

# Covicovey specifics
jam('cov.ing/covey/')
next(block for block in registry if block.labels == ('cloudflare_dns_records', 'this')).attributes[
    'depends_on'
] = [Block('cloudflare_dns_record.this')]
