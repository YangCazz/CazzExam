from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..database import Base


class StudyPlan(Base):
    __tablename__ = "study_plans"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, server_default=func.now())
    phase = Column(String(20), default="")  # 基础/精练/模拟/冲刺
    task_type = Column(String(20), default="")
    target = Column(String(200), default="")
    done = Column(Integer, default=0)
