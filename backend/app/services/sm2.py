from datetime import datetime, timedelta


def sm2_schedule(repetition: int, ease_factor: float, interval_days: int, quality: int):
    """SM-2 简化版：quality 0-5（0=完全忘记，5=完美回忆）"""
    if quality >= 3:
        if repetition == 0:
            interval_days = 1
        elif repetition == 1:
            interval_days = 6
        else:
            interval_days = round(interval_days * ease_factor)
        repetition += 1
    else:
        repetition = 0
        interval_days = 1
    ease_factor = max(1.3, ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
    next_review = datetime.now() + timedelta(days=interval_days)
    return repetition, round(ease_factor, 2), interval_days, next_review
