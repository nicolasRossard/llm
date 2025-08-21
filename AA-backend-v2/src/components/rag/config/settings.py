import yaml
from pathlib import Path

from src.components.rag.config import LLMModelConfig, EmbeddingModelConfig, \
    VectorRepositoryConfig, RAGPConfig

ROOT_DIR = Path(__file__).resolve().parent
PARAMS_FILE = ROOT_DIR / "parameters.yml"


def load_yaml_params():
    """Charge les paramètres YAML par défaut."""
    if PARAMS_FILE.exists():
        with open(PARAMS_FILE, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


yaml_params = load_yaml_params()


def build_config(ConfigClass, yaml_section: dict):
    """Fusionne ENV > YAML > defaults."""
    return ConfigClass(**yaml_section)


# Instanciation
embedding_model_config = build_config(
    EmbeddingModelConfig, yaml_params.get("embedding_model", {})
)
vector_repository_config = VectorRepositoryConfig(
    **yaml_params.get("vector_repository", {}),
    embedding_model_config=embedding_model_config
)
rag_config = build_config(RAGPConfig, yaml_params.get("rag", {}))
llm_model_config = build_config(LLMModelConfig, yaml_params.get("llm_model", {}))


class Settings:
    """Point d’accès unique aux paramètres de l’app."""
    embedding_model = embedding_model_config
    vector_repository = vector_repository_config
    rag = rag_config
    llm = llm_model_config


# Singleton accessible partout
settings = Settings()


if __name__ == "__main__":
    print(f"Embedding Model: {settings.embedding_model}")
    print(f"Vector Repository: {settings.vector_repository}")
    print(f"RAG Config: {settings.rag}")
    print(f"LLM Model: {settings.llm}")
    print("✅ Settings loaded successfully.")

