from llama_cpp import Llama

class LlamaModel:
    def __init__(self, model_path: str, max_length: int, temperature: float, default_promt: str):
        """
        Initialize a LlamaModel instance.

        Args:
            model_path (str): The path to the Llama model.
            max_length (int): The maximum length of the output text.
            temperature (float): The temperature parameter for the model.
            default_promt (str): The default prompt to use when summarizing text.
        """
        self.model_path = model_path
        self.max_length = max_length
        self.temperature = temperature
        self.model = None
        self.load_model()
        self.default_promt = default_promt

    def load_model(self):
        try:
            self.model = Llama(model_path=self.model_path)
            print(f"Model loaded from {self.model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")

    def summarize(self, text: str) -> str:
        """
        Summarize a given piece of text using the loaded Llama model.

        Args:
            text (str): The text to be summarized.

        Returns:
            str: The summarized text.
        """
        if self.model is None:
            raise ValueError("Model is not loaded.")

        params = {
            "prompt": self.default_promt + text,
            "max_tokens": self.max_length,
            "temperature": self.temperature
        }

        summary = self.model(**params).get("choices")[0].get("text", "")
        return summary.strip()