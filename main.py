from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx, os

# -----------------------------
# 建立 FastAPI 應用
# -----------------------------
app = FastAPI()

# -----------------------------
# 掛載 static 資料夾：根網址 (/) 會回傳 static/index.html
# -----------------------------
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# -----------------------------
# (可選) 如果你未來有外部前端跨域，也可以打開這段 CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# -----------------------------
# 外部匯率 API 設定
# -----------------------------
HOST    = "https://api.exchangerate.host"
API_KEY = os.getenv("XRATE_KEY")     # exchangerate.host 免費端點不需要 key，但如果你有其他需求可以放這裡

# -----------------------------
# 代理 /latest：一次抓多幣別匯率，前端呼叫同源 /latest?base=USD&symbols=TWD,JPY...
# -----------------------------
@app.get("/latest")
async def latest(
    base: str    = Query("USD", description="基準貨幣"),
    symbols: str = Query("",    description="目標貨幣，逗號分隔"),
):
    params = {"base": base, "symbols": symbols}
    # 如果有 API_KEY（本例不需），可以放進 params
    if API_KEY:
        params["access_key"] = API_KEY

    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(f"{HOST}/latest", params=params)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        # 印到 Render logs，方便檢查
        print("latest proxy error:", e)
        raise HTTPException(status_code=502, detail="rate-service unavailable")
