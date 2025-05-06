from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx, os

# ----------------------------
# 建立 FastAPI 物件
# ----------------------------
app = FastAPI()

# ----------------------------
# 掛載 static 資料夾：根網址 (/) 直接送出 static/index.html
# ----------------------------
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# ----------------------------
# CORS：允許所有網域對 GET 端點
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ----------------------------
# 外部匯率 API 設定
# ----------------------------
HOST = "https://api.exchangerate.host"
API_KEY = os.getenv("XRATE_KEY")          # 若你的帳號需要 key，請在 Render 環境變數設定

# ----------------------------
# 健康檢查
# ----------------------------
@app.get("/ping")
def ping():
    return {"status": "ok"}

# ----------------------------
# 單一換算 /convert
# ----------------------------
@app.get("/convert")
async def convert(
    from_: str = Query(..., alias="from"),
    to: str = Query(...),
    amount: float = Query(...)
):
    try:
        params = {"from": from_, "to": to, "amount": amount}
        if API_KEY:
            params["access_key"] = API_KEY

        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(f"{HOST}/convert", params=params, follow_redirects=True)
        r.raise_for_status()

        data = r.json()
        if not data.get("success", True) or "result" not in data:
            raise ValueError(data.get("error") or "No result")

        return {"result": data["result"]}

    except Exception as e:
        print("convert error:", e)
        raise HTTPException(status_code=502, detail="rate‑service unavailable")


# ----------------------------
# 代理 /latest：一次抓多幣別即時匯率，避免瀏覽器 CORS
# ----------------------------
@app.get("/latest")
async def latest(base: str = "USD", symbols: str = ""):
    params = {"base": base, "symbols": symbols}
    if API_KEY:
        params["access_key"] = API_KEY

    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(f"{HOST}/latest", params=params)
        r.raise_for_status()
        return r.json()

    except Exception as e:
        print("latest error:", e)
        raise HTTPException(status_code=502, detail="rate‑service unavailable")
