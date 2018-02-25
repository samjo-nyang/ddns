import json
from json import JSONDecodeError
from pathlib import Path

from ddns.utils import DDNSError, is_list_str, is_str


BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / 'config.json'
CONFIG_MAP = {
    'domains': is_list_str,
    'aws_access_key_id': is_str,
    'aws_secret_access_key': is_str,
    'hosted_zone_id': is_str,
}
DATA_PATH = BASE_DIR / 'data.json'
DATA_KEYS = ['checked_at', 'requested_at', 'requested_id', 'synced_at', 'ip_synced', 'ip_pending']


def read_config() -> dict:
    if not CONFIG_PATH.exists():
        raise DDNSError('no such file')

    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.loads(f.read())
    except JSONDecodeError as e:
        raise DDNSError('config/read: failed (invalid json)') from e

    for key, validator in CONFIG_MAP.items():
        if key not in config:
            raise DDNSError(f'config/read: failed (non-existing key "{key}")')
        elif not validator(config[key]):
            raise DDNSError(f'config/read: failed (invalid format of "{key}")')
    return config


def read_data() -> dict:
    if not DATA_PATH.exists():
        raise DDNSError('data/read: failed (no such file)')
        return {}

    try:
        with open(DATA_PATH, 'r') as f:
            raw = json.loads(f.read())
        return {k: str(raw[k]) for k in DATA_KEYS}
    except (JSONDecodeError, KeyError, ValueError) as e:
        raise DDNSError('data/read: failed (malformed)') from e


def get_initial_data() -> dict:
    return {k: '' for k in DATA_KEYS}


def write_data(data: dict):
    with open(DATA_PATH, 'w') as f:
        f.write(json.dumps(data, default=str))
