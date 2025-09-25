from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router as ttt_router

openapi_tags = [
    {
        "name": "System",
        "description": "System and health endpoints.",
    },
    {
        "name": "Tic Tac Toe",
        "description": "Endpoints for creating games, making moves, and fetching status.",
    },
]

app = FastAPI(
    title="Tic Tac Toe API",
    description=(
        "A modern Tic Tac Toe backend built with FastAPI.\n\n"
        "Ocean Professional: Clean design, reliable responses, and clear documentation."
    ),
    version="1.0.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict origins appropriately.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PUBLIC_INTERFACE
@app.get("/", tags=["System"], summary="Health Check")
def health_check():
    """Health check endpoint that returns a simple 'Healthy' message."""
    return {"message": "Healthy", "service": "tic-tac-toe-backend", "status": "ok"}


# Mount Tic Tac Toe API
app.include_router(ttt_router)
