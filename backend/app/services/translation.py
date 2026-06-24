from deep_translator import GoogleTranslator

_translator: GoogleTranslator | None = None


def _get_translator() -> GoogleTranslator:
    global _translator
    if _translator is None:
        _translator = GoogleTranslator(source="auto", target="az")
    return _translator


def translate_to_az(text: str) -> str:
    if not text or len(text.strip()) < 3:
        return text
    try:
        return _get_translator().translate(text[:480])
    except Exception:
        return text


def translate_article(title: str, summary: str) -> tuple[str, str]:
    return translate_to_az(title), translate_to_az(summary) if summary else ""
