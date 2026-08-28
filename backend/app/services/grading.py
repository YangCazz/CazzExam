import json


def grade_choice(question, user_answer) -> bool:
    """单选题判分：user_answer 为选项字符（如 'B'）"""
    try:
        correct = json.loads(question.answer_json) if question.answer_json else None
    except Exception:
        correct = question.answer_json
    if correct is None:
        return False
    return str(user_answer).strip().upper() == str(correct).strip().upper()


def grade_case(question, user_answer_text: str):
    """案例题：返回参考答案供对照（人/AI 判分）"""
    return {"reference": question.answer_json, "user": user_answer_text}
