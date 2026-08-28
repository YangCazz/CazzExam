from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import Base


class WrongQuestion(Base):
    __tablename__ = "wrong_questions"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    first_attempt_id = Column(Integer, nullable=True)
    error_type = Column(String(20), default="")  # 知识性/理解偏差/审题失误/方法错误/其他
    reflection = Column(Text, default="")
    status = Column(String(10), default="new")  # new/reviewing/mastered
    repetition = Column(Integer, default=0)
    interval_days = Column(Integer, default=0)
    ease_factor = Column(Float, default=2.5)
    next_review_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class ReviewLog(Base):
    __tablename__ = "review_logs"
    id = Column(Integer, primary_key=True)
    wrong_question_id = Column(Integer, ForeignKey("wrong_questions.id"), nullable=False)
    reviewed_at = Column(DateTime, server_default=func.now())
    recalled = Column(Integer, default=1)
    note = Column(Text, default="")
