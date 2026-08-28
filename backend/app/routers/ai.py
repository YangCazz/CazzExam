import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import get_db
from ..models.exam import Attempt, Answer
from ..models.question import Question
from ..models.knowledge import KnowledgePoint
from ..config import settings
from ..services.ai_gateway import ai_gateway

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/status")
def ai_status():
    return {
        "available": ai_gateway.available(),
        "base_url": settings.ai_base_url,
        "model": settings.ai_model,
        "hint": "未配置时在 backend/app/config.py 填写 ai_base_url / ai_api_key / ai_model"
    }


@router.post("/grade-essay")
def grade_essay(payload: dict, db: Session = Depends(get_db)):
    """AI 批改论文：按 结构/内容/实践/语言 分档评分 + 建议"""
    if not ai_gateway.available():
        return {"available": False, "scores": None,
                "message": "AI 未配置：请在 backend/app/config.py 填写 ai_base_url / ai_api_key / ai_model"}
    attempt_id = payload["attempt_id"]
    answers = db.scalars(select(Answer).where(Answer.attempt_id == attempt_id)).all()
    essays = []
    for ans in answers:
        q = db.get(Question, ans.question_id)
        if q and q.qtype == "essay":
            essays.append({
                "stem": q.stem,
                "user": json.loads(ans.user_answer_json or "\"\""),
                "reference": json.loads(q.answer_json) if q.answer_json else "",
            })
    if not essays:
        return {"available": True, "scores": None, "message": "该次作答中没有论文题"}
    system = ("你是软考「系统架构设计师」论文阅卷专家。请按四个维度打分（每项满分）："
              "结构结构(25)、内容深度(25)、结合项目实践(30)、语言表达(20)，总分100。"
              "输出 JSON：{\"scores\": {\"structure\":0,\"content\":0,\"practice\":0,\"language\":0},"
              "\"total\":0, \"comments\":\"总评\", \"suggestions\":[\"改进建议\"]}")
    result = ai_gateway.chat_json(system, json.dumps(essays, ensure_ascii=False), timeout=120.0)
    return {"available": True, "scores": result}


@router.post("/generate-questions")
def generate_questions(payload: dict, db: Session = Depends(get_db)):
    """AI 出题（后置功能）：按知识点生成单选题，供人工审核后导入"""
    if not ai_gateway.available():
        return {"available": False, "questions": None,
                "message": "AI 未配置：请在 backend/app/config.py 填写 ai_base_url / ai_api_key / ai_model"}
    kp_ids = payload.get("knowledge_ids", [])
    count = min(payload.get("count", 5), 10)
    names = []
    for kid in kp_ids:
        kp = db.get(KnowledgePoint, kid)
        if kp:
            names.append(kp.name)
    system = ("你是软考「系统架构设计师」命题专家。请针对给定知识点生成单选题。"
              "输出为 JSON 数组，每项包含 stem（题干）、options（四个选项，A. 开头）、"
              "answer（选项字母）、analysis（解析）、knowledge_id（知识点ID整数）字段。")
    user = json.dumps({"knowledge_points": names or ["综合"], "count": count}, ensure_ascii=False)
    result = ai_gateway.chat_json(system, user, timeout=120.0)
    return {"available": True, "questions": result}


@router.post("/analyze-wrong")
def analyze_wrong(payload: dict, db: Session = Depends(get_db)):
    """AI 错因分析：输出归因建议（人工确认后入库）"""
    if not ai_gateway.available():
        return {"available": False, "suggestion": None,
                "message": "AI 未配置，请人工归因"}
    q = db.get(Question, payload["question_id"])
    if not q:
        raise HTTPException(404, "question not found")
    system = ("你是软考辅导老师。根据题目、正确答案与考生错误答案，判断错误类型"
              "（知识性错误/理解偏差/审题失误/方法错误/其他），并给 3 条复习建议。"
              "输出 JSON：{\"error_type\":\"\",\"reason\":\"\",\"suggestions\":[\"\"]}")
    user = json.dumps({
        "stem": q.stem,
        "options": json.loads(q.options_json or "[]"),
        "correct": json.loads(q.answer_json) if q.answer_json else "",
        "user_answer": payload.get("user_answer"),
    }, ensure_ascii=False)
    result = ai_gateway.chat_json(system, user)
    return {"available": True, "suggestion": result}
