from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx, os

# -----------------------------
# 建立 FastAPI 物件
# -----------------------------
app = FastAPI()

# -----------------------------
# CORS：允許所有網域對 GET 端點
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
HOST = "https://api.exchangerate.host"
API_KEY = os.getenv("XRATE_KEY")  # 如有設定就帶入，沒設定就跳過

@app.get("/convert")
async def convert(
    from_: str = Query(..., alias="from"),
    to: str = Query(...),
    amount: float = Query(...),
):
    try:
        params = {"from": from_, "to": to, "amount": amount}
        if API_KEY:
            params["access_key"] = API_KEY

        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(f"{HOST}/convert", params=params, follow_redirects=True)
            r.raise_for_status()

        data = r.json()
        if not data.get("success") or "result" not in data:
            raise ValueError(data.get("error") or "No result")

        return {"result": data["result"]}

    except Exception as e:
        print("convert error:", e)
        raise HTTPException(status_code=502, detail="rate-service unavailable")

@app.get("/latest")
async def latest(base: str = "USD", symbols: str = ""):
    try:
        params = {"base": base, "symbols": symbols}
        if API_KEY:
            params["access_key"] = API_KEY

        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(f"{HOST}/latest", params=params)
            r.raise_for_status()

        return r.json()

    except Exception as e:
        print("latest error:", e)
        raise HTTPException(status_code=502, detail="rate-service unavailable")

# -----------------------------
# 掛載 static 資料夾：放到最後面！
# 只有在找不到上述 API 路由時，才會去抓 index.html、CSS/JS
# -----------------------------
app.mount("/", StaticFiles(directory="static", html=True), name="static")
