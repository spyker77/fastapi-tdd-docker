from typing import Optional

from transformers import Pipeline as PipelineType
from transformers import pipeline

from app.config import get_settings

settings = get_settings()


class LanguageDetector:
    """Language Detector using a transformer model.

    This class provides a language detection feature by utilizing a
    transformer model from the Hugging Face model hub.

    Attributes:
        detector (Optional[PipelineType]): A pipeline object for language detection.
    """

    detector: Optional[PipelineType] = None

    @classmethod
    def get_detector(cls) -> PipelineType:
        """Gets the language detection resources.

        This method checks if the transformer model and tokenizer for language
        detection have been loaded. If not, it loads them. Otherwise, it retrieves
        the loaded resources.

        Returns:
            PipelineType: The loaded or retrieved pipeline object.
        """
        if cls.detector is None:
            cls.detector = pipeline("text-classification", model=settings.LANGUAGE_DETECTION_MODEL)
        return cls.detector

    @classmethod
    def detect(cls, text: str) -> str:
        """Detects the language of the provided text.

        This method utilizes the loaded transformer model to detect the
        language of the provided text.

        Args:
            text (str): The text whose language is to be detected.

        Returns:
            str: The detected language.
        """
        detector = cls.get_detector()
        tokenizer = detector.tokenizer
        input_ids = tokenizer(
            text,
            max_length=256,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )["input_ids"]
        truncated_text = tokenizer.decode(input_ids[0])

        lang_info = detector(truncated_text)
        if not lang_info:
            raise ValueError("Failed to detect language")

        lang_info_item = lang_info[0]
        if not isinstance(lang_info_item, dict):
            raise ValueError("Unexpected type for lang_info_item")

        label = lang_info_item.get("label")
        if label is None:
            raise ValueError("Failed to get label from lang_info_item")

        return label
