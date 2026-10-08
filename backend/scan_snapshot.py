"""Read an already published scan. Never imports or starts the quant engine."""
from __future__ import annotations
import datetime as dt
import os
import json
import math
from pathlib import Path
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StrictBool, StrictInt, ValidationError, model_validator

DEMO_PATH = Path(__file__).resolve().parents[1] / 'shared/scan-demo.json'
FIELDS = json.loads((DEMO_PATH.parent / 'scan-fields.json').read_text(encoding='utf-8'))

class ScanRow(BaseModel):
    model_config = ConfigDict(extra='allow')
    symbol: str = Field(pattern=r'^[A-Z0-9]{3,5}$')
    name: str
    exchange: str
    sector: str | None = None
    recommendation: str | None = None
    passed: StrictBool | None = None
    explanation: str | None = None
    score: float | None = Field(default=None, ge=0, le=100, allow_inf_nan=False, strict=True)
    rating: str | None = None
    holdingSessions: StrictInt | None = Field(default=None, ge=0)
    indexTrend: str | None = None

    @model_validator(mode='after')
    def metric_units(self):
        for field in FIELDS:
            value = getattr(self, field['key'], None)
            if value is None: continue
            if field['format'] in {'pct', 'number', 'price', 'billions'}:
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                    raise ValueError('Numeric metrics must be finite numbers or null')
                if field['format'] == 'price' and value <= 0: raise ValueError('Prices must be positive')
            elif field['key'] == 'gate_pass':
                if not isinstance(value, bool): raise ValueError('Gate must be a boolean')
            elif field['key'] in {'gate_reasons', 'data_quality_flags'}:
                if not isinstance(value,str) and not (isinstance(value,list) and all(isinstance(v,str) for v in value)):
                    raise ValueError('Reasons must be strings or string arrays')
            elif not isinstance(value, str):
                raise ValueError('Labels must be strings or reason arrays')
        return self

class ScanSnapshot(BaseModel):
    runId: str = Field(min_length=1)
    publishedAt: AwareDatetime
    dataAsOf: dt.date
    session: str
    mode: str = Field(pattern=r'^(demo|published)$')
    source: str = Field(min_length=1)
    cadenceMinutes: StrictInt = Field(gt=0)
    universeCount: StrictInt = Field(ge=0)
    rows: list[ScanRow] = Field(max_length=10000)

def load_published_scan() -> dict:
    # If a production path is configured, a failure must NOT turn into demo data.
    configured = os.environ.get('QUANTIK_SCAN_SNAPSHOT')
    path = Path(configured).expanduser() if configured else DEMO_PATH
    try:
        payload = ScanSnapshot.model_validate_json(path.read_text(encoding='utf-8'))
        symbols = [row.symbol for row in payload.rows]
        if len(set(symbols)) != len(symbols) or payload.universeCount < len(symbols):
            raise ValueError('Inconsistent scan coverage')
        data = payload.model_dump(mode='json')
        # Freshness is based on publication, not on the time a visitor clicks.
        age = (dt.datetime.now(dt.timezone.utc) - payload.publishedAt).total_seconds()
        data['isStale'] = age > payload.cadenceMinutes * 60
        return data
    except (OSError, ValueError, ValidationError) as exc:
        raise RuntimeError('Chưa đọc được bản quét đã công bố. Vui lòng thử lại sau.') from exc
