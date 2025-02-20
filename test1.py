  
from http import HTTPStatus
from dashscope.audio.asr import Transcription
import json
import os
from dotenv import load_dotenv
load_dotenv()
# 若没有将API Key配置到环境变量中，需将下面这行代码注释放开，并将apiKey替换为自己的API Key
import dashscope
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

transcribe_response = Transcription.async_call(
    model='paraformer-v2',
    file_urls=['http://brando-test.oss-cn-shanghai.aliyuncs.com/3bd9333d-f8c8-4661-ae17-741423667376.wav'],
    language_hints=['zh', 'en']  # “language_hints”只支持paraformer-v2和paraformer-realtime-v2模型
)
print(transcribe_response)
if transcribe_response.output is None:
    print("Error: transcribe_response.output is None")
    print(f"Status Code: {transcribe_response.status_code}")
    print(f"Error Message: {transcribe_response.message}")
    exit(1)
while True:
    if transcribe_response.output.task_status == 'SUCCEEDED' or transcribe_response.output.task_status == 'FAILED':
        break
    transcribe_response = Transcription.fetch(task=transcribe_response.output.task_id)

if transcribe_response.status_code == HTTPStatus.OK:
    print(json.dumps(transcribe_response.output, indent=4, ensure_ascii=False))
    print('transcription done!')
	

    