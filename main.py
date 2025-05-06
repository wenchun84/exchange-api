from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORS
import httpx, os

# 建立 FastAPI
app = FastAPI()

# 掛載 static 資料夾：根網址 (/) 直接回 static/index.html
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# CORS：允許所有網域對 GET
app.add_middleware(
    CORS,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# 外部匯率 API 設定
HOST    = "https://api.exchangerate.host"
API_KEY = os.getenv("XRATE_KEY")  # 如果有 key 就設定在 Render 環境變數；沒有也沒關係

@app.get("/latest")
async def latest(
    base: str    = Query("USD", description="基準貨幣"),
    symbols: str = Query("",    description="逗號分隔要抓的貨幣列表"),
):
    """
    同源代理 /latest → 呼叫 externel API 抓一次多幣別匯率，回 raw JSON
    前端直接 fetch("/latest?…") 就不會有 CORS 問題
    """
    params = {"base": base, "symbols": symbols}
    if API_KEY:  # 如果有 key，就加上去
        params["access_key"] = API_KEY

    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(f"{HOST}/latest", params=params)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        # 印到 Render log，方便除錯
        print("代理 /latest 發生錯誤：", e)
        raise HTTPException(status_code=502, detail="rate-service unavailable")
