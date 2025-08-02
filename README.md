# 🧠 RAG with Hexagonal Architecture (FastAPI + LLM + Vector DB)

This project implements a **Retrieval-Augmented Generation (RAG)** pipeline using:

- **FastAPI** for the API layer
- **Ollama or OpenAI** as the LLM provider
- **Qdrant** for vector similarity search
- A **hexagonal (ports & adapters)** architecture to ensure modularity, testability, and separation of concerns

---

## 📁 Project Structure

```

rag\_with\_hex/
├── application/
│   └── ports/
│       ├── user\_side/
│       │   ├── usecase/                  # Use case interfaces (e.g., IAnswerQuestion)
│       │   └── usecase\_handler/          # Implementations of use cases (business logic orchestration)
│       └── server\_side/
│           ├── llm\_client.py             # Abstract interface (port) for LLM providers
│           └── vector\_search\_port.py     # Abstract interface (port) for vector search engines like Qdrant
│
├── domain/
│   ├── schema/                           # Domain models: Question, Answer, DocumentChunk (Pydantic)
│   └── service/
│       └── rag\_service.py                # Core RAG logic: retrieve context + generate answer
│
├── infrastructure/
│   └── adapters/
│       ├── user\_side/
│       │   └── rest/
│       │       ├── rag\_routes.py         # FastAPI routes (controllers)
│       │       ├── dto.py                # Input/output Data Transfer Objects (DTOs)
│       │       └── mapper.py             # Mapping between DTOs and domain models
│       │
│       └── server\_side/
│           ├── llm\_openai/
│           │   └── openai\_llm\_client\_adapter.py   # OpenAI implementation of LLM client port
│           ├── llm\_ollama/
│           │   └── ollama\_llm\_client\_adapter.py   # Ollama implementation of LLM client port
│           ├── qdrant/
│           │   └── qdrant\_adapter.py              # Qdrant implementation of vector search port
│           └── persistence/
│               └── log\_repository\_sqlite.py       # Storage adapter (example with SQLite)
│
├── common/
│   └── config.py                        # Shared configuration (constants, env variables, etc.)
│
└── main.py                              # Application entrypoint: sets up FastAPI, wires dependencies

````

---

## ⚙️ Key Concepts

- **Hexagonal Architecture**  
  Ports define *what the system needs*; adapters define *how it's fulfilled*.
  
- **RAG Process**
  1. A question is submitted to the API
  2. Vector search retrieves relevant documents
  3. LLM generates an answer based on those documents
  4. (Optionally) The interaction is logged in a database

- **Swappable Adapters**
  - You can switch between OpenAI and Ollama LLM clients
  - You can replace Qdrant with another vector store easily

---

## 🏁 Getting Started

1. Clone the repository
2. Install packages

```bash
docker compose up
make run
````

---

## 🧪 Testing Without Real Qdrant

A fake implementation of `QdrantAdapter` is provided for local development/testing without connecting to a real vector DB.

---

## 📌 License

MIT – feel free to use and adapt.

```
