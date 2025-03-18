import logging
from pathlib import Path
from typing import List

from deepeval import evaluate
from deepeval.metrics import HallucinationMetric
from deepeval.models import GPTModel
from deepeval.test_case import LLMTestCase

from ..config.openai_client import get_openai_vision_prediction
from ..config.settings import settings
from ..load_attack_images.load_txt import load_text_descriptions
from ..make_images.image_utils import imgfile2base64

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=settings.logging_level, format="%(asctime)s - %(levelname)s - %(message)s"
)


def create_text_test_cases(
    words_file: Path, vision_prompt: str = "What do you see?", test_model: str = "llava"
) -> List[LLMTestCase]:
    words_file = settings.data_path / "txt" / words_file
    text_descriptions = load_text_descriptions(words_file)
    logger.info(f"Evaluating text images for {test_model}")

    test_cases = []
    for desc in text_descriptions:
        base64_image = imgfile2base64(desc.image_path)
        model_output = get_openai_vision_prediction(
            base64_image, vision_prompt, model=test_model
        )

        ground_truth = f"The image contains word '{desc.text}' written in black text on white background."

        test_case = LLMTestCase(
            input=vision_prompt,
            actual_output=model_output,
            expected_output=ground_truth,
            context=[ground_truth],
        )
        test_cases.append(test_case)
        logger.info(
            f"Created test case: {desc.image_path} - Model's {test_model} output: {model_output}"
        )
    return test_cases


def evaluate_text_images(
    words_file: Path, vision_prompt: str = "What do you see?", test_model: str = "llava"
):
    test_cases = create_text_test_cases(words_file, vision_prompt, test_model)

    judge_model = GPTModel(
        model=settings.judge_model_name, _openai_api_key=settings.openai_api_key
    )
    metric = HallucinationMetric(model=judge_model)
    return evaluate(test_cases=test_cases, metrics=[metric], run_async=True)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate text images")
    parser.add_argument("--words_file", type=Path, default=None)
    parser.add_argument(
        "--vision_prompt", type=str, default="What do you see?", help="Vision prompt"
    )
    parser.add_argument("--test_model", type=str, default="llava", help="Test model")
    args = parser.parse_args()

    if args.words_file is not None:
        evaluate_text_images(args.words_file, args.vision_prompt, args.test_model)
    else:
        raise ValueError("No words file provided")


if __name__ == "__main__":
    main()
