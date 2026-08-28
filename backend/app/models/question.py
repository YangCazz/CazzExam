from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from ..database import Base


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    qtype = Column(String(10), default="choice")  # choice/case/essay
    subject = Column(Integer, default=1)  # 1 综合知识 2 案例分析 3 论文
    stem = Column(Text, nullable=False)
    options_json = Column(Text, default="[]")
    answer_json = Column(Text, default="")
    analysis = Column(Text, default="")
    difficulty = Column(Integer, default=3)  # 1-5
    source_type = Column(String(10), default="real")  # real/self/ai
    source_year = Column(Integer, nullable=True)
    status = Column(String(10), default="active")


class QuestionItem(Base):
    __tablename__ = "question_items"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    seq = Column(Integer, default=1)
    stem = Column(Text, default="")
    answer = Column(Text, default="")
    score = Column(Integer, default=0)


class QuestionKnowledge(Base):
    __tablename__ = "question_knowledge"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    knowledge_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=False)
    weight = Column(Float, default=1.0)
