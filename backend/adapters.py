"""
Chỗ DUY NHẤT bạn cần nối vào code Python gốc (quant_pipeline.py, quant_visual.py, vnstock_data...).
Mỗi hàm bên dưới đang là bản demo chạy được để thử giao diện. Thay phần thân bằng lời gọi thật,
giữ nguyên chữ ký hàm và định dạng dữ liệu trả về thì server.py và React không phải sửa.
"""
from __future__ import annotations
import hashlib, random, time
from pathlib import Path

# Canonical demo catalog shared with React. Replace this adapter for a real feed.
import copy, json
import os
from market_snapshot import load_snapshot
SAMPLE = json.loads((Path(__file__).resolve().parents[1] / "shared/market-demo.json").read_text())
MODE = "demo"
DATA_VERSION = SAMPLE["version"]
MODEL_VERSION = "placeholder-v3-visuals"

def load_board(group: str = "ALL", exchange: str | None = None, sector: str | None = None) -> dict:
    configured = os.environ.get('QUANTIK_MARKET_SNAPSHOT')
    data = load_snapshot(configured) if configured else copy.deepcopy(SAMPLE)
    chosen_exchange = exchange or (group if group in {"HOSE", "HNX", "UPCOM"} else None)
    data["instruments"] = [i for i in data["instruments"] if (not chosen_exchange or i["exchange"] == chosen_exchange) and (not sector or i["sectorId"] == sector)]
    syms = {i["symbol"] for i in data["instruments"]}
    data["quotes"] = [q for q in data["quotes"] if q["symbol"] in syms]
    return data

def sector_summary(exchange: str | None = None, sector: str | None = None, snapshot: dict | None = None) -> list[dict]:
    data = snapshot if snapshot is not None else load_board(exchange=exchange, sector=sector)
    result = []
    for s in data["sectors"]:
        syms = {i["symbol"] for i in data["instruments"] if i["sectorId"] == s["id"]}
        qs = [q for q in data["quotes"] if q["symbol"] in syms]
        if not qs: continue
        returns = [q["price"] / q["ref"] - 1 for q in qs if q.get("price") is not None and q.get("ref", 0) > 0]
        values = [q["value"] for q in qs if q.get("value") is not None]
        result.append({"sectorId": s["id"], "name": s["name"], "count": len(syms), "valid": len(returns), "mean": sum(returns)/len(returns) if returns else None, "value": sum(values) if values else None, "valueCoverage": len(values), "method": "equal-weight-return", "mode": data['mode']})
    return result

# ---- 2. Pipeline quant ----------------------------------------------------
MODULES = [
    {"id": "trend", "name": "Xu hướng", "desc": "Giá so với SMA 20 / 50 / 200"},
    {"id": "mom", "name": "Động lượng", "desc": "RSI 14 và MACD"},
    {"id": "flow", "name": "Dòng tiền", "desc": "Chaikin Money Flow 20 phiên"},
    {"id": "rs", "name": "Sức mạnh tương đối", "desc": "So với VN-Index, hệ số beta"},
    {"id": "hmm", "name": "Trạng thái thị trường (HMM)", "desc": "Tăng, đi ngang hoặc giảm"},
    {"id": "garch", "name": "Biến động (GARCH)", "desc": "Độ bền biến động, ATR"},
    {"id": "mc", "name": "Mô phỏng Monte Carlo", "desc": "1.000 đường giá, 10 phiên"},
    {"id": "risk", "name": "Rủi ro và sụt giảm", "desc": "Max drawdown, VaR, CVaR"},
    {"id": "decision", "name": "Tổng hợp quyết định", "desc": "Điểm, cắt lỗ, chốt lời"},
]

def load_context(symbol: str) -> dict:
    """Nạp dữ liệu giá của mã + VN-Index vào một dict dùng chung cho các module.
    TODO: gọi hàm tải dữ liệu trong quant_pipeline.py / crawl_data.py."""
    return {"symbol": symbol, "quote": next(q for q in SAMPLE["quotes"] if q["symbol"] == symbol)}

def run_module(module_id: str, ctx: dict) -> dict:
    """Chạy MỘT module và ghi kết quả vào ctx.
    TODO: map từng id sang engine thật của bạn, ví dụ:
      hmm   -> HMMEngine        garch -> GARCHEngine      mc   -> FcastEngine (Monte Carlo)
      risk  -> RiskEng (ATR stop, tối ưu expectancy)      decision -> AdaptiveScorer
    Lưu ý: engine nặng (HMM, GARCH) nên chạy được độc lập; module sau có thể đọc ctx của module trước."""
    time.sleep(0.4)  # demo
    ctx[module_id] = {"ok": True}
    return ctx

def summarize(ctx: dict) -> dict:
    """Các con số hiển thị ở hàng đầu bảng kết quả (đơn vị: nghìn đồng)."""
    q = ctx["quote"]
    p = q["price"] / 1000
    # Layout sample only: this is not a financial model or executable strategy.
    return {"score": q["score"], "action": "Theo dõi (mô phỏng)", "entry": p,
            "stop": round(p * .95, 2), "tp1": round(p * 1.1, 2), "tp2": round(p * 1.15, 2),
            "net_r": 2.0, "atr_pct": None}

def metric_results(ctx: dict) -> list[dict]:
    definitions = json.loads((Path(__file__).resolve().parents[1] / "src/content/metrics.json").read_text())
    return [{"id": m["id"], "value": None, "unit": "", "status": "not_computed", "methodId": m["methodId"], "provenance": "reference-only"} for m in definitions]

def research_payload(ctx: dict) -> dict | None:
    """Replace with precomputed quant_visuals aggregates from the real pipeline.

    The current adapter is explicitly demo. Do not derive live simulation/regime
    charts from scores or summary metrics when raw inputs were not preserved.
    """
    if MODE != 'demo': return ctx.get('research')
    data = json.loads((Path(__file__).resolve().parents[1] / 'shared/research-demo.json').read_text(encoding='utf-8'))
    data['symbol'] = ctx['symbol']
    price = ctx['quote']['price']
    if price is None or price <= 0:
        data['cone'] = []; data['regime'] = []
        return data
    for point in data['cone']:
        for key in ['p05','p25','p50','p75','p95']: point[key] *= price
    for point in data['regime']: point['price'] *= price
    return data


def render_image(ctx: dict, path: Path) -> None:
    """Dựng ảnh tổng quan 6 panel và lưu ra `path` (PNG).
    TODO: gọi hàm vẽ trong quant_visual.py, ví dụ fig.savefig(path, dpi=160, facecolor=fig.get_facecolor())."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(12, 5), facecolor="#0b1017")
    ax.set_facecolor("#0b1017"); ax.axis("off")
    ax.text(0.5, 0.5, f"Ảnh demo cho {ctx['symbol']}\nThay bằng quant_visual.py", color="#f5a623", ha="center", va="center", fontsize=18)
    fig.savefig(path, dpi=110, facecolor=fig.get_facecolor()); plt.close(fig)
