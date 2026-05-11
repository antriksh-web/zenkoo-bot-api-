import random


SLANG_SNIPPETS = ["fr", "nah", "bro", "real", "lowkey", "ngl", "idk"]
EMOJIS = ["??", "??", "??", "??", "??", "??", "??"]


def maybe_typo(text: str) -> str:
    if len(text) < 6:
        return text
    idx = random.randint(1, len(text) - 2)
    return text[:idx] + text[idx + 1] + text[idx] + text[idx + 2:]


def stylize_text(text: str, typing_style: str, grammar_quality: float, emoji_usage: float) -> str:
    out = text
    if typing_style in {"lazy_lowercase", "typo_heavy"}:
        out = out.lower()
    if typing_style == "dry":
        out = out.split(".")[0].strip() + "."
    if typing_style == "hyper_emoji" and random.random() < emoji_usage:
        out = f"{out} {random.choice(EMOJIS)}{random.choice(EMOJIS)}"
    elif random.random() < emoji_usage * 0.7:
        out = f"{out} {random.choice(EMOJIS)}"

    if grammar_quality < 0.45 and random.random() < 0.35:
        out = maybe_typo(out)

    if random.random() < 0.2:
        out = f"{random.choice(SLANG_SNIPPETS)} {out}"

    return out.strip()
