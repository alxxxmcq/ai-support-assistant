from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json

from prompts import build_client_response, build_manager_tip

app = FastAPI(
    title="AI Support Assistant",
    description="Simple customer support assistant with a small JSON knowledge base.",
    version="1.0.0",
)

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_BASE_PATH = BASE_DIR / "knowledge_base.json"


class ClientRequest(BaseModel):
    message: str


class AssistantResponse(BaseModel):
    client_response: str
    manager_tip: str
    matched_topic: str | None = None


def load_knowledge_base() -> list[dict]:
    """Load knowledge base from JSON file."""
    try:
        with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("Knowledge base must contain a list of records.")

        return data
    except FileNotFoundError as exc:
        raise RuntimeError("knowledge_base.json was not found.") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("knowledge_base.json contains invalid JSON.") from exc


KNOWLEDGE_BASE = load_knowledge_base()


def find_relevant_article(message: str) -> dict | None:
    """
    Very simple retrieval:
    returns the knowledge-base article with the largest number
    of matching keywords.
    """
    message_lower = message.lower()

    best_article = None
    best_score = 0

    for article in KNOWLEDGE_BASE:
        keywords = article.get("keywords", [])
        score = sum(1 for keyword in keywords if keyword.lower() in message_lower)

        if score > best_score:
            best_score = score
            best_article = article

    return best_article


@app.get("/")
def root():
    return {
        "service": "AI Support Assistant",
        "status": "ok",
        "docs": "/docs",
    }


@app.post("/analyze", response_model=AssistantResponse)
def analyze_request(request: ClientRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(status_code=400, detail="Message must not be empty.")

    article = find_relevant_article(message)

    if article:
        answer = article["answer"]
        topic = article["topic"]
        upsell = article.get("upsell", "")
    else:
        answer = (
            "В базе знаний нет точного ответа на этот вопрос. "
            "Рекомендуем уточнить детали у менеджера."
        )
        topic = None
        upsell = (
            "Уточните потребность клиента и предложите подходящий продукт "
            "или дополнительную услугу только после выяснения контекста."
        )

    return AssistantResponse(
        client_response=build_client_response(message, answer),
        manager_tip=build_manager_tip(message, upsell),
        matched_topic=topic,
    )
