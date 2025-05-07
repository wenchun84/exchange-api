# src/main.py

from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx, os

# ——————————————
# 建立 FastAPI app
# ——————————————
app = FastAPI()

# ——————————————
# 把 static 目錄 mount 在 /
# （這樣造訪 根網址 就會回傳 static/index.html）
# ——————————————
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# ——————————————
# 加上 CORS middleware，允許前端同源呼叫 GET /latest
# ——————————————
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ——————————————
# 外部匯率 API 設定
# ——————————————
HOST    = "https://api.exchangerate.host"
API_KEY = os.getenv("XRATE_KEY", "")   # 若沒有 key，留空字串

# ——————————————
# 代理 /latest：前端呼叫同源 /latest?base=...&symbols=...
# 由後端去請求真正的 exchangerate.host/latest
# 把結果原封不動回傳給前端
# ——————————————
@app.get("/latest")
async def latest(
    base: str    = Query("USD", description="基準貨幣"),
    symbols: str = Query("",    description="逗號分隔的欲查詢貨幣列表"),
):
    # 組參數
    params = {"base": base, "symbols": symbols}
    if API_KEY:
        params["access_key"] = API_KEY

    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(f"{HOST}/latest", params=params)
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        # 印錯誤到 Render logs，前端顯示 502
        print("latest proxy error:", e)
        raise HTTPException(status_code=502, detail="rate-service unavailable")

    # 確認回來的 JSON 裡面有 rates
    if "rates" not in data:
        raise HTTPException(status_code=502, detail="no rates in response")

    return data
