import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from models import Session, Interview, init_db
from utils import AudioProcessor
from config import Config
import uuid
import subprocess
import wave

app = Flask(__name__)
CORS(app)

# 确保上传目录存在
os.makedirs(Config.VOICE_UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def check_wav_file(file_path):
    """检查WAV文件是否有效"""
    try:
        with wave.open(file_path, 'rb') as wav_file:
            # 获取音频文件的参数
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            frame_rate = wav_file.getframerate()
            frames = wav_file.getnframes()
            duration = frames / float(frame_rate)
            
            print(f"WAV file info: channels={channels}, sample_width={sample_width}, "
                  f"frame_rate={frame_rate}, frames={frames}, duration={duration:.2f}s")
            
            # 检查是否是有效的音频文件
            return frames > 0 and duration > 0.1  # 至少0.1秒
    except Exception as e:
        print(f"Error checking WAV file: {str(e)}")
        return False

def convert_to_wav(input_path):
    """将音频文件转换为wav格式"""
    output_path = os.path.splitext(input_path)[0] + '.wav'
    try:
        # 使用ffmpeg转换音频格式，添加更多的音频处理参数
        subprocess.run([
            'ffmpeg', '-i', input_path,
            '-acodec', 'pcm_s16le',  # 16位PCM编码
            '-ar', '16000',          # 16kHz采样率
            '-ac', '1',              # 单声道
            '-af', 'silenceremove=1:0:-50dB',  # 移除静音部分
            '-af', 'volume=2.0',     # 提高音量
            '-y',                    # 覆盖已存在的文件
            output_path
        ], check=True, capture_output=True)

        # 检查生成的WAV文件是否有效
        if not check_wav_file(output_path):
            print("Generated WAV file is invalid")
            return None

        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error converting audio: {e.stderr.decode()}")
        return None
    except Exception as e:
        print(f"Error converting audio: {str(e)}")
        return None

@app.route('/api/interview', methods=['POST'])
def process_interview():
    try:
        print("Processing interview request...")
        
        if 'audio' not in request.files:
            print("No audio file in request")
            return jsonify({'error': 'No audio file'}), 400
        
        file = request.files['audio']
        if file.filename == '':
            print("No selected file")
            return jsonify({'error': 'No selected file'}), 400
        
        if not file or not allowed_file(file.filename):
            print(f"Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type'}), 400

        # 保存用户音频文件
        filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(file.filename)[1])
        local_file_path = os.path.join(Config.VOICE_UPLOAD_FOLDER, filename)
        print(f"Saving file to: {local_file_path}")
        file.save(local_file_path)
        
        # 转换音频格式为wav
        wav_file_path = convert_to_wav(local_file_path)
        if not wav_file_path:
            return jsonify({'error': 'Failed to convert audio format'}), 500
            
        # 检查转换后的文件大小
        file_size = os.path.getsize(wav_file_path)
        if file_size < 1024:  # 小于1KB的文件可能是无效的
            print(f"Converted file is too small: {file_size} bytes")
            return jsonify({'error': 'Audio file is too small or empty'}), 400
        
        processor = AudioProcessor()
        
        # 上传到OSS
        print("Uploading to OSS...")
        file_url = processor.upload_to_oss(wav_file_path)
        if not file_url:
            print("Failed to upload file to OSS")
            return jsonify({'error': 'Failed to upload file to OSS'}), 500
        
        # 语音转文本
        print("Converting speech to text...")
        user_text = processor.speech_to_text(file_url)
        if not user_text:
            print("Speech to text conversion failed")
            return jsonify({'error': 'Speech to text failed'}), 500
        
        # 获取AI回复
        print("Getting AI response...")
        ai_response = processor.chat_with_ai(user_text)
        if not ai_response:
            print("Failed to get AI response")
            return jsonify({'error': 'Failed to get AI response'}), 500
        
        # 生成AI语音回复
        print("Converting AI response to speech...")
        ai_audio_filename = str(uuid.uuid4()) + '.wav'
        ai_audio_path = os.path.join(Config.VOICE_UPLOAD_FOLDER, ai_audio_filename)
        if not processor.text_to_speech(ai_response, ai_audio_path):
            print("Text to speech conversion failed")
            return jsonify({'error': 'Text to speech failed'}), 500
        
        # 上传AI音频到OSS
        print("Uploading AI response audio to OSS...")
        ai_audio_url = processor.upload_to_oss(ai_audio_path)
        if not ai_audio_url:
            print("Failed to upload AI audio to OSS")
            return jsonify({'error': 'Failed to upload AI audio'}), 500
        
        # 保存到数据库
        print("Saving to database...")
        try:
            session = Session()
            interview = Interview(
                user_audio_path=file_url,
                user_text=user_text,
                ai_response_text=ai_response,
                ai_audio_path=ai_audio_url
            )
            session.add(interview)
            session.commit()
            session.close()
        except Exception as e:
            print(f"Database error: {str(e)}")
            return jsonify({'error': 'Database error'}), 500
        
        # 清理临时文件
        try:
            os.remove(local_file_path)
            os.remove(wav_file_path)
        except Exception as e:
            print(f"Error cleaning up temporary files: {str(e)}")
        
        print("Interview processing completed successfully")
        return jsonify({
            'user_text': user_text,
            'ai_response': ai_response,
            'ai_audio_url': ai_audio_url
        })
        
    except Exception as e:
        print(f"Error processing interview: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        session = Session()
        interviews = session.query(Interview).order_by(Interview.created_at.desc()).all()
        result = [{
            'id': interview.id,
            'user_text': interview.user_text,
            'ai_response': interview.ai_response_text,
            'ai_audio_url': interview.ai_audio_path,
            'created_at': interview.created_at.isoformat()
        } for interview in interviews]
        session.close()
        return jsonify(result)
    except Exception as e:
        print(f"Error getting history: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 