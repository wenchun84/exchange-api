from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 放心，只有 GET，風險極低
    allow_methods=["GET"],
    allow_headers=["*"],
)
HOST = "https://api.exchangerate.host"
API_KEY = os.getenv("XRATE_KEY")      # 從 Render 環境變數讀金鑰


@app.get("/")                         # 健康檢查
def root():
    return {"status": "ok"}


@app.get("/convert")
async def convert(
    from_: str = Query(..., alias="from"),
    to: str = Query(...),
    amount: float = Query(...)
):
    try:
        params = {"from": from_, "to": to, "amount": amount}
        if API_KEY:
            params["access_key"] = API_KEY       # 把金鑰帶進去

        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get(f"{HOST}/convert", params=params, follow_redirects=True)
        r.raise_for_status()

        data = r.json()
        if not data.get("success") or "result" not in data:
            raise ValueError(data.get("error") or "no result")

        return {"result": data["result"]}

    except Exception as e:
        print("convert error:", e)                # 印在 Render log
        raise HTTPException(status_code=502, detail="rate‑service unavailable")
