"""Serve cov.ing/covey as Cloudflare Workers Assets.

cov.ing is shared, so manage only covicovey's Worker, its /covey/* routes, and a
preview-subdomain DNS record. mublog owns the zone root, its route, and the
append-slash ruleset.
"""

from os import environ
from pathlib import Path

from helicopyter import only_main, provider, resource, terraform

# I'd use literals if this were a private repository
account_id = environ['CLOUDFLARE_ACCOUNT_ID']
zone_id = environ['CLOUDFLARE_ZONE_ID']

terraform.backend('s3')(
    bucket='terraform',
    endpoints={'s3': f'https://{account_id}.r2.cloudflarestorage.com'},
    key='covicovey.tfstate',
    region='auto',
    workspace_key_prefix='covicovey',
    skip_credentials_validation='true',
    skip_metadata_api_check='true',
    skip_region_validation='true',
    skip_requesting_account_id='true',
    skip_s3_checksum='true',
    use_path_style='true',
)
terraform.required_providers(cloudflare={'source': 'cloudflare/cloudflare', 'version': '5.25.0'})

provider.cloudflare()

resource.cloudflare_workers_script('this')(
    account_id=account_id,
    assets={'config': {'not_found_handling': 'none'}, 'directory': '../../../site'},
    compatibility_date='2026-08-28',
    content=(Path(__file__).parent / 'worker.js').read_text(),
    main_module='worker.js',
    script_name='covicovey-${terraform.workspace}',
)

resource.cloudflare_workers_route('preview')(
    depends_on=['cloudflare_workers_script.this'],
    pattern='${terraform.workspace}.cov.ing/covey/*',
    script='covicovey-${terraform.workspace}',
    zone_id=zone_id,
)

resource.cloudflare_dns_record('preview')(
    content='100::',
    name='${terraform.workspace}',
    proxied=True,
    ttl=1,
    type='AAAA',
    zone_id=zone_id,
)

with only_main():
    resource.cloudflare_workers_route('production')(
        depends_on=['cloudflare_workers_script.this'],
        pattern='cov.ing/covey/*',
        script='covicovey-${terraform.workspace}',
        zone_id=zone_id,
    )
