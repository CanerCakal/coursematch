import re

from app.models.course import Course


STOP_WORDS = {
    "ve",
    "veya",
    "ile",
    "bu",
    "bir",
    "için",
    "olarak",
    "olan",
    "derste",
    "ders",
    "dersi",
    "temel",
    "giriş",
    "the",
    "and",
    "or",
    "to",
    "of",
    "in",
    "a",
    "an",
    "is",
    "are",
}

KEYWORD_ALIASES = {
    "programlama": "programming",
    "programlamaya": "programming",
    "programlamayi": "programming",
    "programming": "programming",

    "algoritma": "algorithm",
    "algoritmalar": "algorithm",
    "algorithms": "algorithm",
    "algorithm": "algorithm",

    "veri": "data",
    "data": "data",

    "yapilari": "structures",
    "structures": "structures",
    "structure": "structures",

    "fonksiyon": "function",
    "fonksiyonlar": "function",
    "functions": "function",
    "function": "function",

    "dongu": "loop",
    "donguler": "loop",
    "loops": "loop",
    "loop": "loop",

    "kosul": "condition",
    "kosullar": "condition",
    "conditionals": "condition",
    "condition": "condition",

    "degisken": "variable",
    "degiskenler": "variable",
    "variables": "variable",
    "variable": "variable",

    "liste": "list",
    "listeler": "list",
    "lists": "list",
    "list": "list",

    "dosya": "file",
    "dosyalar": "file",
    "files": "file",
    "file": "file",

    "python": "python",
}


def normalize_text(text: str | None) -> str:
    if not text:
        return ""

    text = text.lower()
    text = text.replace("ı", "i")
    text = text.replace("ğ", "g")
    text = text.replace("ü", "u")
    text = text.replace("ş", "s")
    text = text.replace("ö", "o")
    text = text.replace("ç", "c")

    return text


def extract_keywords(text: str | None) -> set[str]:
    normalized_text = normalize_text(text)

    words = re.findall(r"[a-zA-Z0-9]+", normalized_text)

    keywords = {
        word
        for word in words
        if len(word) >= 4 and word not in STOP_WORDS
    }

    return {
        KEYWORD_ALIASES.get(keyword, keyword)
        for keyword in keywords
    }


def course_to_text(course: Course) -> str:
    parts = [
        course.name,
        course.description,
        course.weekly_plan,
        course.learning_outcomes,
        course.resources,
    ]

    return " ".join(part for part in parts if part)


def calculate_keyword_similarity(
    source_course: Course,
    target_course: Course,
) -> tuple[float, list[str]]:
    source_text = course_to_text(source_course)
    target_text = course_to_text(target_course)

    source_keywords = extract_keywords(source_text)
    target_keywords = extract_keywords(target_text)

    if not source_keywords or not target_keywords:
        return 0.0, []

    matched_keywords = sorted(source_keywords.intersection(target_keywords))
    all_keywords = source_keywords.union(target_keywords)

    similarity = len(matched_keywords) / len(all_keywords) * 100

    return similarity, matched_keywords


def calculate_course_similarity(
    source_course: Course,
    target_course: Course,
) -> dict:
    keyword_similarity, matched_keywords = calculate_keyword_similarity(
        source_course,
        target_course,
    )

    ects_match = (
        source_course.ects is not None
        and target_course.ects is not None
        and source_course.ects == target_course.ects
    )

    credit_match = (
        source_course.credit is not None
        and target_course.credit is not None
        and source_course.credit == target_course.credit
    )

    score = keyword_similarity

    if ects_match:
        score += 10

    if credit_match:
        score += 10

    score = min(score, 100)
    score = round(score, 2)

    if score >= 80:
        summary = "Dersler yüksek seviyede benzer görünüyor."
    elif score >= 50:
        summary = "Dersler orta seviyede benzer görünüyor."
    elif score >= 25:
        summary = "Dersler düşük-orta seviyede benzer görünüyor."
    else:
        summary = "Dersler düşük seviyede benzer görünüyor."

    return {
        "source_course_id": source_course.id,
        "target_course_id": target_course.id,
        "similarity_score": score,
        "ects_match": ects_match,
        "credit_match": credit_match,
        "matched_keywords": matched_keywords[:20],
        "summary": summary,
    }