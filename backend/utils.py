import os
import uuid
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider
import dashscope
from dashscope.audio.asr import Transcription
from dashscope.audio.tts_v2 import SpeechSynthesizer
from config import Config
from http import HTTPStatus
import json
import time
import requests

class AudioProcessor:
    def __init__(self):
        # 设置 dashscope API key
        dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
        print(f"DashScope API Key: {dashscope.api_key}")  # 打印API key用于调试
        
        # 初始化语音合成器
        self.synthesizer = SpeechSynthesizer(model="cosyvoice-v1", voice="loongbella")
        
        # 设置OSS
        try:
            # 使用V4签名认证
            self.auth = oss2.ProviderAuthV4(EnvironmentVariableCredentialsProvider())
            endpoint = f"https://oss-{Config.OSS_REGION}.aliyuncs.com"
            print(f"OSS Endpoint: {endpoint}")
            
            # 创建Bucket实例，指定存储空间的名称和Region信息
            self.bucket = oss2.Bucket(
                self.auth, 
                endpoint, 
                Config.OSS_BUCKET,
                region=Config.OSS_REGION
            )
            print("OSS initialized successfully")
        except Exception as e:
            print(f"Error initializing OSS: {str(e)}")
            raise

    def upload_to_oss(self, local_file_path):
        """上传文件到OSS"""
        try:
            print(f"Uploading file: {local_file_path}")
            
            # 检查文件是否存在
            if not os.path.exists(local_file_path):
                print(f"File not found: {local_file_path}")
                return None
                
            # 检查文件大小
            file_size = os.path.getsize(local_file_path)
            print(f"File size: {file_size} bytes")
            
            # 生成唯一的文件名
            file_name = str(uuid.uuid4()) + os.path.splitext(local_file_path)[1]
            print(f"Generated OSS object name: {file_name}")
            
            # 上传文件
            self.bucket.put_object_from_file(file_name, local_file_path)
            
            # 生成文件URL
            file_url = f"https://{Config.OSS_BUCKET}.oss-{Config.OSS_REGION}.aliyuncs.com/{file_name}"
            print(f"File uploaded successfully. URL: {file_url}")
            return file_url
        except Exception as e:
            print(f"Error uploading to OSS: {str(e)}")
            return None

    def get_transcription_result(self, transcription_url):
        """从转录URL获取结果"""
        try:
            print(f"Fetching transcription from URL: {transcription_url}")
            response = requests.get(transcription_url)
            if response.status_code == 200:
                result = response.json()
                print(f"Transcription response: {json.dumps(result, indent=2)}")
                
                # 检查并提取文本内容
                if 'transcripts' in result and result['transcripts']:
                    for transcript in result['transcripts']:
                        if 'sentences' in transcript:
                            for sentence in transcript['sentences']:
                                if 'text' in sentence:
                                    return sentence['text']
                print("No text found in transcription response")
                return None
            else:
                print(f"Failed to fetch transcription. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error getting transcription result: {str(e)}")
            print(f"Full error details: {str(e.__class__.__name__)}: {str(e)}")
            return None

    def speech_to_text(self, file_url):
        """语音转文本"""
        try:
            print(f"Starting speech to text conversion for URL: {file_url}")
            
            # 调用语音识别
            response = Transcription.async_call(
                model='paraformer-v2',
                file_urls=[file_url],
                language_hints=['zh', 'en']
            )
            print(f"Initial response: {response}")
            
            if response.status_code != HTTPStatus.OK:
                print(f"Error in initial call: Status {response.status_code}")
                return None
            
            if response.output is None:
                print("Error: response.output is None")
                return None
            
            task_id = response.output.task_id
            print(f"Task ID: {task_id}")
            
            # 等待任务完成
            max_retries = 30
            retry_count = 0
            while retry_count < max_retries:
                # 获取任务状态
                response = Transcription.fetch(task=task_id)
                print(f"Fetch response: {response}")
                
                if not hasattr(response, 'output') or response.output is None:
                    print("Invalid response format")
                    retry_count += 1
                    time.sleep(1)
                    continue
                
                if response.status_code != HTTPStatus.OK:
                    print(f"Error in fetch: Status {response.status_code}")
                    retry_count += 1
                    time.sleep(1)
                    continue
                
                # 将响应转换为字典以便访问
                response_dict = json.loads(str(response))
                print(f"Response dict: {json.dumps(response_dict, indent=2)}")
                
                if response_dict['output']['task_status'] == 'SUCCEEDED':
                    print("Task succeeded")
                    # 检查结果列表
                    results = response_dict['output'].get('results', [])
                    if results:
                        for result in results:
                            transcription_url = result.get('transcription_url')
                            if transcription_url:
                                print(f"Found transcription URL: {transcription_url}")
                                # 获取转录结果
                                text = self.get_transcription_result(transcription_url)
                                if text:
                                    print(f"Final transcription result: {text}")
                                    return text
                    print("No transcription URL found in response")
                    return None
                elif response_dict['output']['task_status'] == 'FAILED':
                    print("Task failed")
                    return None
                elif response_dict['output']['task_status'] in ['PENDING', 'RUNNING']:
                    print(f"Task status: {response_dict['output']['task_status']}, waiting...")
                    time.sleep(1)
                    retry_count += 1
                else:
                    print(f"Unknown task status: {response_dict['output']['task_status']}")
                    return None
            
            print("Task timed out")
            return None
            
        except Exception as e:
            print(f"Error in speech_to_text: {str(e)}")
            print(f"Full error details: {str(e.__class__.__name__)}: {str(e)}")
            return None

    def text_to_speech(self, text, output_path):
        """文本转语音"""
        try:
            print(f"Converting text to speech: {text}")
            
            # 使用cosyvoice-v1模型生成语音
            audio = self.synthesizer.call(text)
            print(f"[Metric] requestId: {self.synthesizer.get_last_request_id()}, "
                  f"first package delay ms: {self.synthesizer.get_first_package_delay()}")
            
            # 保存音频文件
            with open(output_path, 'wb') as f:
                f.write(audio)
            print(f"Speech file saved to: {output_path}")
            return True
                
        except Exception as e:
            print(f"Error in text_to_speech: {str(e)}")
            print(f"Full error details: {str(e.__class__.__name__)}: {str(e)}")
            return False

    def chat_with_ai(self, user_input):
        """与AI模型对话"""
        try:
            print(f"Sending message to AI: {user_input}")
            response = dashscope.Generation.call(
                model='qwen-plus',
                messages=[
                    {'role': 'system', 'content': '你是一个专业的面试官，请用专业、友好的语气进行面试。'},
                    {'role': 'user', 'content': user_input}
                ]
            )
            
            if response.status_code == HTTPStatus.OK:
                result = response.output.text
                print(f"AI response: {result}")
                return result
            
            print(f"Chat failed with status: {response.status_code}")
            print(f"Error message: {response.message}")
            return "抱歉，我现在无法回答您的问题。"
        except Exception as e:
            print(f"Error in chat_with_ai: {str(e)}")
            return "抱歉，系统出现了问题。" 