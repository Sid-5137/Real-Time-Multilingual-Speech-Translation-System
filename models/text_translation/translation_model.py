from transformers import MarianMTModel, MarianTokenizer

class TranslationModel:
    """Translate text from one language to another."""
    def __init__(self, src_lang="fr", tgt_lang="en"):
        # model_name = f'Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}'
        model_name = f'Helsinki-NLP/opus-mt-ROMANCE-en'
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name)

    def translate(self, text):
        inputs = self.tokenizer(text, return_tensors="pt")
        translated = self.model.generate(**inputs)
        return self.tokenizer.decode(translated[0], skip_special_tokens=True)
