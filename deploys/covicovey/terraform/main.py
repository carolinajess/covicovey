"""Serve cov.ing/covey as Cloudflare Workers Assets.

cov.ing is shared: mublog owns the zone root, its route, and the append-slash ruleset.
"""

from os import environ

from helicopyter import Block, data, registry, resource
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
# Main adopts the record use-jam created; remove after main first deploys
zone_id = environ['CLOUDFLARE_ZONE_ID']
existing = data.cloudflare_dns_records.existing(
    lifecycle=Block('lifecycle')(
        postcondition=Block('postcondition')(
            condition=Block('terraform.workspace != "main" || length(self.result) > 0'),
            error_message='Proxied *.cov.ing AAAA record not found for main to adopt',
        )
    ),
    name={'exact': '*.cov.ing'},
    type='AAAA',
    zone_id=zone_id,
)
Block('import')(
    for_each=Block('terraform.workspace == "main" ? {adopt = true} : {}'),
    id=Block(f'"{zone_id}/${{data.cloudflare_dns_records.existing.result[0].id}}"'),
    to=Block('cloudflare_dns_record.this[0]'),
)

# Covicovey specifics
jam('cov.ing/covey/')
next(block for block in registry if block.labels == ('cloudflare_dns_records', 'this')).attributes[
    'depends_on'
] = [Block('cloudflare_dns_record.this')]
