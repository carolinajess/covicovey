"""Serve cov.ing/covey as Cloudflare Workers Assets.

cov.ing is shared: mublog owns the zone root, its route, and the append-slash ruleset.
"""

from os import environ

from helicopyter import Block, data, registry, resource
from helicopyter.cloudflare import jam
from stacks.base import provide

provide('cloudflare/cloudflare', '5.27.0-startup.1')

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
# Main adopts the record use-jam created; remove after main first deploys
existing = data.cloudflare_dns_records.existing(
    name={'exact': '*.cov.ing'}, type='AAAA', zone_id=environ['CLOUDFLARE_ZONE_ID']
)
Block('import')(
    for_each=Block('terraform.workspace == "main" ? {adopt = true} : {}'),
    id=Block(
        f'"{environ["CLOUDFLARE_ZONE_ID"]}/${{data.cloudflare_dns_records.existing.result[0].id}}"'
    ),
    to=Block('cloudflare_dns_record.this[0]'),
)

# Covicovey specifics
jam('cov.ing/covey/')
next(block for block in registry if block.labels == ('cloudflare_dns_records', 'this')).attributes[
    'depends_on'
] = [Block('cloudflare_dns_record.this')]
