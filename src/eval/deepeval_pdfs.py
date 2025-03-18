import logging
from typing import List

from deepeval import evaluate
from deepeval.metrics import HallucinationMetric
from deepeval.models import GPTModel
from deepeval.test_case import LLMTestCase

from src.config.openai_client import get_openai_vision_prediction
from src.config.settings import settings
from src.load_attack_images.load_pdfs import load_pdf_descriptions
from src.make_images.image_utils import imgfile2base64

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=settings.logging_level, format="%(asctime)s - %(levelname)s - %(message)s"
)


def create_pdf_test_cases(
    vision_prompt: str = "What do you see?", test_model: str = "llava"
) -> List[LLMTestCase]:
    pdf_descriptions = load_pdf_descriptions()
    logger.info(f"Evaluating PDFs for {test_model}")

    test_cases = []
    for pdf_description in pdf_descriptions:
        base64_image = imgfile2base64(pdf_description.image_path)
        model_output = get_openai_vision_prediction(
            base64_image, vision_prompt, model=test_model
        )

        test_case = LLMTestCase(
            input=vision_prompt,
            actual_output=model_output,
            expected_output=pdf_description.description,
            context=[pdf_description.description],
        )
        test_cases.append(test_case)
        logging.info(
            f"Created test case: {pdf_description.image_path} - Model's {test_model} output: {model_output}"
        )
    return test_cases


def evaluate_test_cases(
    test_cases: List[LLMTestCase], metric_classes=[HallucinationMetric]
):
    judge_model = GPTModel(
        model=settings.judge_model_name, _openai_api_key=settings.openai_api_key
    )
    metrics = [metric_class(model=judge_model) for metric_class in metric_classes]
    return evaluate(test_cases=test_cases, metrics=metrics, run_async=True)


def evaluate_pdfs(vision_prompt: str = "What do you see?", test_model: str = "llava"):
    test_cases = create_pdf_test_cases(vision_prompt, test_model)
    return evaluate_test_cases(test_cases)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate PDFs")
    parser.add_argument(
        "--vision_prompt", type=str, default="What do you see?", help="Vision prompt"
    )
    parser.add_argument("--test_model", type=str, default="llava", help="Test model")
    args = parser.parse_args()

    evaluate_pdfs(args.vision_prompt, args.test_model)


if __name__ == "__main__":
    main()
