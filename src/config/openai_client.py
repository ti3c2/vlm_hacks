import logging

from openai import OpenAI

from src.config.settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=settings.logging_level, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_openai_vision_prediction(
    image_base64: str,
    vision_prompt: str,
    model: str = "llava",
) -> str:
    """Sends image and vision prompt to OpenAI and returns the prediction"""
    # Use ollama if not gpt else openai
    base_url = settings.openai_custom_endpoint if not model.startswith("gpt") else None
    client: OpenAI = OpenAI(base_url=base_url, api_key=settings.openai_api_key)
    logger.info(f"Sending query to OpenAI on {base_url} to {model}")

    response = client.chat.completions.create(
        model=model,
        messages=[
            # {"role": "system", "content": "You are an image recognition assistant."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": vision_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                    },
                ],
            }
        ],
    )
    response_content = response.choices[0].message.content
    if response_content is None:
        logger.error("OpenAI API returned None")
        # raise ValueError("OpenAI API returned None")
        return "ERROR"
    return response_content
