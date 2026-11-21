"""Module 2 - text cleaning. Keeps technical symbols such as C++, C#, .NET, CI/CD."""
import re

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
URL = re.compile(r"(https?://\S+|www\.\S+|linkedin\.com\S*)", re.I)
PHONE = re.compile(
    r"(?<!\d)(?:\+?\d{1,3}[\s-]?)?\d{10}(?!\d)"
    r"|(?<!\d)\d{3}[\s-]\d{3}[\s-]\d{4}(?!\d)"
    r"|\+\d{1,3}[\s-]?\d{3,5}[\s-]?\d{3,5}(?:[\s-]?\d{2,5})?"
)


def remove_personal_info(text: str) -> str:
    """Strip contact details so they can never influence scoring (fairness rule)."""
    for pattern in (EMAIL, URL, PHONE):
        text = pattern.sub(" ", text)
    return text


def clean_text(text: str) -> str:
    """Lowercase, drop contact info and noisy symbols, collapse whitespace."""
    text = text.replace("\u2022", " ").replace("\u00a0", " ")
    text = remove_personal_info(text).lower()
    text = re.sub(r"[^a-z0-9+#./\-\n ]", " ", text)  # keep + # . / - for c++ c# .net ci/cd
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()
