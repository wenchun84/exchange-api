from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx, os

# ----------------------------
# 建立 FastAPI 物件
# ----------------------------
app = FastAPI()

# ----------------------------
# 掛載 static 資料夾
# 讓根網址 (/) 或 /static/ 能直接送出 HTML/CSS/JS
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
API_KEY = os.getenv("XRATE_KEY")          # 若你有設定金鑰，就會讀到；沒有則為 None

# ----------------------------
# 健康檢查
# ----------------------------
@app.get("/ping")
def ping():
    return {"status": "ok"}

# ----------------------------
# 匯率換算端點
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
        if not data.get("success") or "result" not in data:
            raise ValueError(data.get("error") or "No result")

        return {"result": data["result"]}

    except Exception as e:
        # 印到 Render Logs，方便除錯
        print("convert error:", e)
        raise HTTPException(status_code=502, detail="rate‑service unavailable")
