from fastapi import FastAPI, Query
import httpx

app = FastAPI()
HOST = "https://api.exchangerate.host"

@app.get("/convert")
async def convert(
    from_: str = Query(..., alias="from"),
    to: str = Query(...),
    amount: float = Query(...)
):
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{HOST}/convert",
                        params={"from": from_, "to": to, "amount": amount})
    return {"result": r.json()["result"]}
