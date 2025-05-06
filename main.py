from fastapi import FastAPI, Query, HTTPException
import httpx, os                     # ← 加入 os

app = FastAPI()
HOST = "https://api.exchangerate.host"
API_KEY = os.getenv("XRATE_KEY")     # ← 讀環境變數

...

async with httpx.AsyncClient(timeout=8) as c:
    params = {"from": from_, "to": to, "amount": amount}
    if API_KEY:                      # ← 把金鑰加進參數
        params["access_key"] = API_KEY
    r = await c.get(f"{HOST}/convert", params=params, follow_redirects=True)
