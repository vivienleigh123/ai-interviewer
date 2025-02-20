from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

Base = declarative_base()
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

class Interview(Base):
    __tablename__ = 'interviews'

    id = Column(Integer, primary_key=True)
    user_audio_path = Column(String(255))  # 用户音频文件路径
    user_text = Column(Text)  # 用户语音转文字
    ai_response_text = Column(Text)  # AI回复文字
    ai_audio_path = Column(String(255))  # AI音频文件路径
    created_at = Column(DateTime, default=datetime.utcnow)

# 创建数据库表
def init_db():
    Base.metadata.create_all(engine) 