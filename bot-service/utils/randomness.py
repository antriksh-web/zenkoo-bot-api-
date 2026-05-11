import random


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def chance(probability: float) -> bool:
    return random.random() < clamp(probability)


def jitter(value: float, amount: float = 0.15) -> float:
    delta = value * amount
    return value + random.uniform(-delta, delta)
