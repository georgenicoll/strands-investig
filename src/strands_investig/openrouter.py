import os

from strands.models import OpenAIModel

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL_ID = "openai/gpt-6-luna"


def openrouter_model(model_id: str = OPENROUTER_MODEL_ID) -> OpenAIModel:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY environment variable is not set.")

    return OpenAIModel(
        client_args={
            "base_url": OPENROUTER_BASE_URL,
            "api_key": api_key,
        },
        model_id=model_id,
    )
