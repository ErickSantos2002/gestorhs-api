"""
Middleware CORS
"""
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings


def setup_cors(app):
    """Configura CORS"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
