"""Read a complete external listing/quote snapshot independently of the scan."""
import json
import math
import re
from pathlib import Path

PRICE_KEYS = {'price','ref','ceil','floor','open','high','low'}
VOLUME_KEYS = {'vol','value','lastVolume','foreignBuy','foreignSell','foreignRoom'}

def validate_snapshot(data):
    if not isinstance(data, dict) or data.get('units', {}).get('price') != 'VND':
        raise ValueError('Expected VND snapshot envelope')
    if not isinstance(data.get('instruments'), list) or not isinstance(data.get('quotes'), list):
        raise ValueError('Listing and quotes required')
    symbols = [i['symbol'] for i in data['instruments']]
    if len(symbols) != len(set(symbols)) or not all(isinstance(s,str) and re.fullmatch(r'[A-Z0-9]{1,12}',s) for s in symbols):
        raise ValueError('Invalid listing')
    listed = set(symbols)
    quoted = set()
    for q in data['quotes']:
        if q['symbol'] not in listed or q['symbol'] in quoted: raise ValueError('Unknown or duplicate quote')
        quoted.add(q['symbol'])
        for key in PRICE_KEYS | VOLUME_KEYS:
            value = q.get(key)
            if value is None: continue
            if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value < 0:
                raise ValueError('Invalid quote number')
            if key in PRICE_KEYS and value == 0: q[key] = None
    data.setdefault('mode', 'unknown')
    data.setdefault('source', 'Snapshot từ nguồn ngoài')
    # A recent API fetch does not prove the provider is real-time.
    if data['mode'] == 'live' and data.get('verifiedLive') is not True: data['mode'] = 'unknown'
    data.setdefault('sectors', [])
    data.setdefault('classification', {'mode':'unknown'})
    return data

def load_snapshot(path):
    try:
        return validate_snapshot(json.loads(Path(path).expanduser().read_text(encoding='utf-8')))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise RuntimeError('Chưa đọc được snapshot bảng điện. Giữ bản công bố gần nhất hoặc thử lại sau.') from exc
