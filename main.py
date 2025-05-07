# src/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import httpx, os

app = FastAPI()

# CORS (如果你只用同源內部呼叫，其實可以捨棄)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# 外部匯率 API 設定
HOST    = "https://api.exchangerate.host"
API_KEY = os.getenv("XRATE_KEY", "")  # render 上設定環境變數 XRATE_KEY

# 1) /latest 動態端點，一定要先宣告
@app.get("/latest")
async def latest(base: str = "USD", symbols: str = ""):
    params = {"base": base}
    if symbols:
        params["symbols"] = symbols
    if API_KEY:
        params["access_key"] = API_KEY

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{HOST}/latest", params=params)
            r.raise_for_status()
            return JSONResponse(content=r.json())
    except Exception as e:
        # 在 Render 的 log 裡就能看到錯在哪
        print("proxy /latest error:", e)
        raise HTTPException(status_code=502, detail="rate-service unavailable")


# 2) 直接把 index.html 回傳給根目錄
@app.get("/")
async def root():
    return FileResponse("static/index.html")


# 3) catch-all，讓 SPA 前端路由（如果有）也能直接回 index.html
@app.get("/{full_path:path}")
async def spa(full_path: str):
    return FileResponse("static/index.html")
