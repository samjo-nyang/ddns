import boto3
import requests
from botocore.exceptions import ClientError
from requests.exceptions import RequestException

from ddns.utils import DDNSError


def fetch_ip():
    try:
        return requests.get('https://api.ipify.org').text.strip()
    except RequestException as e:
        raise DDNSError('ip/fetch: failed') from e


def get_route53(aws_access_key_id: str, aws_secret_access_key: str):
    return boto3.client('route53', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)


def is_synced(route53, request_id: str) -> bool:
    try:
        return route53.get_change(Id=request_id)['ChangeInfo']['Status'] == 'INSYNC'
    except (ClientError, KeyError) as e:
        raise DDNSError('dns/query: failed') from e


def update_dns(route53, hosted_zone_id: str, domains: list, ip: str) -> str:
    try:
        return route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Changes': [{
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': domain,
                        'Type': 'A',
                        'TTL': 60,
                        'ResourceRecords': [{
                            'Value': ip,
                        }],
                    },
                } for domain in domains],
            }
        )['ChangeInfo']['Id']
    except (ClientError, KeyError) as e:
        raise DDNSError('dns/update: failed') from e
