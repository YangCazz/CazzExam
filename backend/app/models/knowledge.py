from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from ..database import Base


class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), default="")
    subject = Column(Integer, default=0)  # 0=通用 1=综合知识 2=案例分析 3=论文
    description = Column(Text, default="")
    memo = Column(Text, default="")
    card = Column(Text, default="")  # 知识点速查卡:结构化 JSON(系统预置,只读,不入 PUT 白名单)
    mastery = Column(Float, default=0.0)  # 0-100 计算值


class KnowledgeRelation(Base):
    __tablename__ = "knowledge_relations"
    id = Column(Integer, primary_key=True)
    from_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=False)
    to_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=False)
    relation_type = Column(String(20), default="related")  # prerequisite/related/contains/conflicts/backbone
    note = Column(String(200), default="")
