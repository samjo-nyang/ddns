from datetime import datetime

import click

from ddns.api import fetch_ip, get_route53, is_synced, update_dns
from ddns.io import get_initial_data, read_config, read_data, write_data
from ddns.utils import DDNSError, print_error, print_info, print_ok, print_warn


def check(config: dict, data: dict) -> (int, dict):
    route53 = get_route53(config['aws_access_key_id'], config['aws_secret_access_key'])
    requested_id = data['requested_id']
    if requested_id:
        try:
            synced = is_synced(route53, requested_id)
        except DDNSError as e:
            print_error(e)
            return 1, data

        if not synced:
            print_warn('dns/sync: not yet :(')
            return 1, data
        print_ok('dns/sync: done')
        data['requested_at'] = ''
        data['requested_id'] = ''
        data['synced_at'] = datetime.now()
        data['ip_synced'] = data['ip_pending']
        data['ip_pending'] = ''

    try:
        ip_now = fetch_ip()
    except DDNSError as e:
        print_error(e)
        return 1, data

    ip_synced = data['ip_synced']
    print_info(f'ip/fetch: {ip_now}')
    if ip_synced == ip_now:
        print_ok('ip/check: not changed')
        return 0, data

    print_warn(f'ip/check: changed ({ip_synced} -> {ip_now})')
    try:
        requested_id = update_dns(route53, config['hosted_zone_id'], config['domains'], ip_now)
    except DDNSError as e:
        print_error(e)
        return 1, data

    print_warn(f'dns/update: requested ({requested_id})')
    data['requested_at'] = datetime.now()
    data['requested_id'] = requested_id
    data['ip_pending'] = ip_now
    return 0, data


@click.command()
@click.option('--quite', is_flag=True)
def main(quite):
    ''' Simple Handmade DDNS using Route53 '''
    try:
        config = read_config()
    except DDNSError as e:
        print_error(e)
        exit(1)

    try:
        data = read_data()
    except DDNSError as e:
        print_warn(str(e))
        data = get_initial_data()

    exit_code, data = check(config, data)
    data['checked_at'] = datetime.now()
    write_data(data)
    exit(exit_code)


if __name__ == '__main__':
    main()
