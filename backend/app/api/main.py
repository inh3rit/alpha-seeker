from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import positions, rankings, recommendations, stocks

app = FastAPI(
    title="Alpha Seeker API",
    description="A股智能推荐系统 API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommendations.router, prefix="/api/recommendations", tags=["推荐"])
app.include_router(positions.router, prefix="/api/positions", tags=["持仓"])
app.include_router(rankings.router, prefix="/api/rankings", tags=["排行榜"])
app.include_router(stocks.router, prefix="/api/stocks", tags=["股票"])


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
