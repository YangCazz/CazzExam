from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from ..database import Base


class EssayMaterial(Base):
    __tablename__ = "essay_materials"
    id = Column(Integer, primary_key=True)
    category = Column(String(20), default="项目经历")  # 项目经历/架构决策/技术点/范文
    title = Column(String(200), default="")
    content = Column(Text, default="")
    tags = Column(String(200), default="")


class Adr(Base):
    __tablename__ = "adr"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    status = Column(String(20), default="proposed")
    context = Column(Text, default="")
    decision = Column(Text, default="")
    alternatives = Column(Text, default="")
    consequences = Column(Text, default="")
    date = Column(DateTime, server_default=func.now())
