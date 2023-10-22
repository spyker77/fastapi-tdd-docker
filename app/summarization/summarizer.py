from typing import Optional

from transformers import MBartForConditionalGeneration, MBartTokenizer


class Summarizer:
    """A class used to encapsulate summarization functionality.

    Attributes:
        model (Optional[MBartForConditionalGeneration]): A transformer model used for text summarization.
        tokenizer (Optional[MBartTokenizer]): A tokenizer used to process text for the transformer model.
    """

    model: Optional[MBartForConditionalGeneration] = None
    tokenizer: Optional[MBartTokenizer] = None

    @classmethod
    def load_resources(cls, model_name: str) -> None:
        """Loads the tokenizer and model resources if they are not already loaded.

        Args:
            model_name (str): The name or path of the pre-trained model.
        """
        if cls.model is None or cls.tokenizer is None:
            cls.tokenizer = MBartTokenizer.from_pretrained(model_name)
            cls.model = MBartForConditionalGeneration.from_pretrained(model_name)

    @classmethod
    def summarize(cls, text: str, model_name: str) -> str:
        """Summarizes the provided text using the loaded transformer model.

        Args:
            text (str): The text to summarize.
            model_name (str): The name or path of the pre-trained model.

        Returns:
            str: The summarized text.
        """
        cls.load_resources(model_name)

        if cls.tokenizer is None or cls.model is None:
            raise ValueError("Resources not loaded")

        input_ids = cls.tokenizer(
            text,
            max_length=600,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )["input_ids"]

        output_ids = cls.model.generate(input_ids, no_repeat_ngram_size=4)[0]

        return cls.tokenizer.decode(output_ids, skip_special_tokens=True)
