import random


def reading_delay_ms(message_len: int, attention: float) -> int:
    base = 300 + message_len * 18
    modifier = 1.6 - attention
    return int(base * modifier + random.randint(0, 300))


def thinking_delay_ms(confidence: float, tension: float) -> int:
    base = 500 + int((1 - confidence) * 1200)
    return int(base + tension * 400 + random.randint(100, 900))


def typing_delay_ms(text_len: int, typing_style: str) -> int:
    style_wpm = {
        "lazy_lowercase": 45,
        "dry": 70,
        "hyper_emoji": 55,
        "ranting": 35,
        "typo_heavy": 40,
    }
    wpm = style_wpm.get(typing_style, 50)
    words = max(1, text_len // 5)
    ms = (words / wpm) * 60_000
    return int(ms + random.randint(150, 1200))
