from abc import ABC, abstractmethod

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

from app.config import get_settings

settings = get_settings()


class Summarizer(ABC):
    """Abstract base class for Summarizer.

    The Summarizer class serves as the base class for different language-specific
    summarizer implementations. It handles the loading of the transformer model
    and tokenizer based on the provided model name.

    Attributes:
        tokenizer (AutoTokenizer): Tokenizer for text processing.
        model (AutoModelForSeq2SeqLM): Transformer model for summarization.
    """

    def __init__(self, model_name_or_path: str):
        """Initializes the tokenizer and model.

        Args:
            model_name_or_path (str): The name of the pre-trained model or path to load.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name_or_path)

    @abstractmethod
    def summarize(self, text: str) -> str:
        """Abstract method to summarize text.

        Args:
            text (str): Text to summarize.

        Returns:
            str: Summarized text.
        """
        pass


class EnglishSummarizer(Summarizer):
    """English text summarizer.

    This summarizer uses a simplified pipeline approach for English text.
    """

    def summarize(self, text: str) -> str:
        """Summarizes English text.

        Args:
            text (str): Text to summarize.

        Returns:
            str: Summarized text.
        """
        summarization_pipeline = pipeline("summarization", model=self.model, tokenizer=self.tokenizer)
        summary = summarization_pipeline(text, max_length=200, min_length=50, do_sample=False)
        return summary[0]["summary_text"]


class RussianSummarizer(Summarizer):
    """Russian text summarizer.

    This summarizer uses a detailed generate and decode approach for Russian text.
    """

    def summarize(self, text: str) -> str:
        """Summarizes Russian text.

        Args:
            text (str): Text to summarize.

        Returns:
            str: Summarized text.
        """
        input_ids = self.tokenizer(
            text,
            max_length=600,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )["input_ids"]

        output_ids = self.model.generate(input_ids, no_repeat_ngram_size=4)[0]
        return self.tokenizer.decode(output_ids, skip_special_tokens=True)


class SummarizerFactory:
    """Factory class to provide summarizer instances based on language.

    The SummarizerFactory class manages the creation and caching of Summarizer
    instances for different languages. It ensures that only one summarizer
    instance is created per language, thereby conserving resources.

    Attributes:
        _instances (dict[str, Summarizer]): Dictionary to hold created summarizer instances.
    """

    _instances: dict[str, Summarizer] = {}

    @classmethod
    def get_summarizer(cls, lang: str) -> Summarizer:
        """Gets a summarizer for the specified language.

        This method checks if a summarizer instance for the specified language
        already exists. If not, it creates a new instance, caches it, and returns it.
        If an instance already exists, it returns the cached instance.

        Args:
            lang (str): Language code (e.g., 'en' for English, 'ru' for Russian).

        Returns:
            Summarizer: Summarizer instance for the specified language.
        """
        if lang not in cls._instances:
            model_name = cls.get_model_name(lang)
            summarizer_class = RussianSummarizer if lang == "ru" else EnglishSummarizer
            cls._instances[lang] = summarizer_class(model_name)
        return cls._instances[lang]

    @staticmethod
    def get_model_name(lang: str) -> str:
        """Gets the model name based on the specified language.

        Args:
            lang (str): Language code (e.g., 'en' for English, 'ru' for Russian).

        Returns:
            str: Model name for the specified language.
        """
        model_mapping = {
            "en": settings.SUMMARIZER_MODEL_EN,
            "ru": settings.SUMMARIZER_MODEL_RU,
        }
        if lang not in model_mapping:
            raise ValueError(f"Unsupported language: {lang}")
        return model_mapping[lang]
