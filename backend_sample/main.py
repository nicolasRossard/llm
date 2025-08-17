from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from config import SETTINGS


def custom_generate_unique_id(route: APIRoute) -> str:
    # Ensure route.tags is not empty and route.name is defined
    if route.tags and route.name:
        return f"{route.tags[0]}-{route.name}"
    return route.name or f"unnamed-route-{route.path_format}"


app = FastAPI(
    title=SETTINGS.PROJECT_NAME,
    openapi_url=f"{SETTINGS.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set up CORS middleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider restricting in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.components.chatbot.infrastructure import __routers__ as chatbot_routers

for router in chatbot_routers:
    app.include_router(router, prefix=SETTINGS.API_V1_STR)
