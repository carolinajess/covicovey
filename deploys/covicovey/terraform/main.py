"""Serve cov.ing/covey as Cloudflare Workers Assets.

cov.ing is shared: mublog owns the zone root, its route, and the append-slash ruleset.
"""

from helicopyter import Block
from helicopyter.cloudflare import jam
from stacks.base import provide

provide('cloudflare/cloudflare', '5.27.0-startup.1')

# Homework owns the proxied wildcard previews require; forget it without destroying
Block('removed')(**{
    'from': Block('cloudflare_dns_record.this'),
    'lifecycle': Block('lifecycle')(destroy=False),
})

# Covicovey specifics
jam('cov.ing/covey/')
