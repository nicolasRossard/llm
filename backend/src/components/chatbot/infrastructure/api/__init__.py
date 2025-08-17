from .v1.chatbot_routes import chatbot_rag_router

# Export routers as actual APIRouter objects
__routers__ = [
    chatbot_rag_router
]

__all__ = ["__routers__"]
