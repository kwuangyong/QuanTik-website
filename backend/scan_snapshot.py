"""Read an already published scan. Never imports or starts the quant engine."""
from __future__ import annotations
import datetime as dt
import os
from pathlib import Path
from pydantic import AwareDatetime, BaseModel, Field, StrictBool, StrictInt, ValidationError

DEMO_PATH = Path(__file__).resolve().parents[1] / 'shared/scan-demo.json'

class ScanRow(BaseModel):
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
