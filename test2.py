# coding=utf-8

import dashscope
from dashscope.audio.tts_v2 import *
import os
from dotenv import load_dotenv
load_dotenv()
# 若没有将API Key配置到环境变量中，需将下面这行代码注释放开，并将apiKey替换为自己的API Key
import dashscope
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

model = "cosyvoice-v1"
voice = "loongbella"

synthesizer = SpeechSynthesizer(model=model, voice=voice)
audio = synthesizer.call("你叫什么?")
print('[Metric] requestId: {}, first package delay ms: {}'.format(
    synthesizer.get_last_request_id(),
    synthesizer.get_first_package_delay()))

with open('output1.mp3', 'wb') as f:
    f.write(audio)