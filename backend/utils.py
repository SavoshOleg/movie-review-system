import hashlib
import re

POSITIVE_WORDS = {
    "гарний": 2, "чудовий": 3, "цікавий": 2, "сильний": 2,
    "неймовірний": 3, "сподобався": 2, "класний": 2, "якісний": 2,
    "атмосферний": 2, "рекомендую": 3, "вражаючий": 3, "емоційний": 2,
    "захоплюючий": 3, "динамічний": 2, "добрий": 1, "кращий": 3,
    "прекрасний": 3, "відмінний": 3, "топ": 3
}

NEGATIVE_WORDS = {
    "поганий": -2, "нудний": -2, "слабкий": -2, "жахливий": -3,
    "нецікавий": -2, "розчарував": -3, "затягнутий": -2,
    "провальний": -3, "скучний": -2, "погано": -2,
    "не сподобався": -3, "слабко": -2, "незрозумілий": -1,
    "хаотичний": -2, "переоцінений": -2
}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def analyze_sentiment(text: str) -> tuple[str, str, int, int]:
    lower_text = text.lower()
    score = 0
    found_keywords = []

    for word, value in POSITIVE_WORDS.items():
        if word in lower_text:
            score += value
            found_keywords.append(word)

    for word, value in NEGATIVE_WORDS.items():
        if word in lower_text:
            score += value
            found_keywords.append(word)

    words = re.findall(r"[а-яА-ЯіІїЇєЄґҐa-zA-Z]+", lower_text)
    normalized_score = max(-10, min(10, score))
    positivity_percent = int(round(((normalized_score + 10) / 20) * 100))

    if normalized_score >= 3:
        sentiment = "Позитивний"
    elif normalized_score <= -3:
        sentiment = "Негативний"
    else:
        sentiment = "Нейтральний"

    if not found_keywords:
        candidate_words = sorted(set(words), key=len, reverse=True)
        found_keywords = candidate_words[:3]

    return sentiment, ", ".join(found_keywords), normalized_score, positivity_percent
