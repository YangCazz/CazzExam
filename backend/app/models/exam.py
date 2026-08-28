from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import Base


class PaperTemplate(Base):
    __tablename__ = "paper_templates"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    subject = Column(Integer, default=1)
    duration_min = Column(Integer, default=150)
    config_json = Column(Text, default="{}")


class Paper(Base):
    __tablename__ = "papers"
    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, ForeignKey("paper_templates.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class PaperQuestion(Base):
    __tablename__ = "paper_questions"
    id = Column(Integer, primary_key=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    seq = Column(Integer, default=1)


class Attempt(Base):
    __tablename__ = "attempts"
    id = Column(Integer, primary_key=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=True)
    mode = Column(String(10), default="practice")  # practice/mock/wrong
    started_at = Column(DateTime, server_default=func.now())
    finished_at = Column(DateTime, nullable=True)
    total_score = Column(Float, default=0.0)


class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True)
    attempt_id = Column(Integer, ForeignKey("attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    user_answer_json = Column(Text, default="")
    is_correct = Column(Integer, default=0)
    time_spent = Column(Integer, default=0)
    ai_feedback_json = Column(Text, default="")
