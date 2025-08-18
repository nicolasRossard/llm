from .v1.rag_routes import rag_router

# Export routers as actual APIRouter objects
__routers__ = [
    rag_router
]

__all__ = ["__routers__"]
