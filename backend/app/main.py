from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, sales, location

app = FastAPI(
    title="DatabuzzOxxo API",
    description="API for DatabuzzOxxo application",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(sales.router, prefix="/api", tags=["sales"])
app.include_router(location.router, prefix="/api", tags=["location"])

@app.get("/")
async def root():
    return {"message": "Welcome to DatabuzzOxxo API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

