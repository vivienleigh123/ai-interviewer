import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 数据库配置
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = 3306
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '985211'
    MYSQL_DB = 'ai_interview'
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OSS配置
    OSS_REGION = "cn-shanghai"
    OSS_BUCKET = "brando-test"
    
    # 语音文件存储路径
    VOICE_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'my_voice')
    
    # 允许上传的文件类型
    ALLOWED_EXTENSIONS = {'wav', 'mp3', 'webm'} 