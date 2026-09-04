from fastapi import FastAPI

app = FastAPI(title="HRIDAY", version="0.1.0", description="Sovereign industrial P&ID intelligence workbench")

@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "hriday-api"}
