from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database import Base


class StudyProfile(Base):
    __tablename__ = "study_profiles"
    id = Column(Integer, primary_key=True)
    certification = Column(String(100), default="系统架构设计师")
    target_date = Column(String(10), default="")
    weekly_minutes = Column(Integer, default=240)
    timezone = Column(String(50), default="Asia/Shanghai")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class LearningTask(Base):
    __tablename__ = "learning_tasks"
    id = Column(Integer, primary_key=True)
    task_date = Column(String(10), nullable=False, index=True)
    task_type = Column(String(20), nullable=False)  # review/practice/material
    subject = Column(Integer, default=0)
    target_id = Column(Integer, nullable=True)
    title = Column(String(200), nullable=False)
    reason = Column(String(300), default="")
    completion_hint = Column(String(200), default="")
    estimated_minutes = Column(Integer, default=15)
    status = Column(String(20), default="generated")  # generated/in_progress/completed/skipped/expired
    skip_reason = Column(String(200), default="")
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)

