<template>
  <div class="interview-container">
    <div class="chat-layout">
      <div class="interviewer-section">
        <DigitalHuman ref="digitalHuman" @session-ready="onDigitalHumanReady" @session-error="handleSessionError" />
      </div>
      <div class="chat-section">
        <div class="messages" ref="messagesContainer">
          <div v-for="(message, index) in messages" :key="index" :class="['message', message.type]">
            <div class="message-bubble">
              <div class="message-text">{{ message.text }}</div>
              <div v-if="message.audioUrl" class="audio-player">
                <audio :src="message.audioUrl" controls ref="audioPlayer" @loadeddata="playAudio($event, index)"></audio>
              </div>
            </div>
          </div>
        </div>
        <div class="controls">
          <el-button 
            type="primary" 
            :class="{ 'recording': isRecording }"
            @mousedown="startRecording" 
            @mouseup="stopRecording"
            @mouseleave="stopRecording"
            :disabled="!isDigitalHumanReady"
          >
            <i class="el-icon-microphone"></i>
            {{ isRecording ? '松开结束录音' : '按住说话' }}
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import DigitalHuman from '../components/DigitalHuman.vue';

export default {
  name: 'Interview',
  components: {
    DigitalHuman
  },
  data() {
    return {
      messages: [],
      isRecording: false,
      mediaRecorder: null,
      audioChunks: [],
      isDigitalHumanReady: false
    }
  },
  methods: {
    onDigitalHumanReady() {
      this.isDigitalHumanReady = true;
      console.log('isDigitalHumanReady:', this.isDigitalHumanReady); // 添加调试信息
      this.$message.success('数字人准备就绪');
    },
    handleSessionError(error) {
      console.error('Digital human session error:', error);
      this.$message.error('数字人初始化失败，请刷新页面重试');
    },
    playAudio(event, index) {
      // 只有当这是最新的消息时才自动播放
      if (index === this.messages.length - 1) {
        event.target.play();
      }
    },
    async startRecording() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        this.mediaRecorder = new MediaRecorder(stream, {
          mimeType: 'audio/webm'
        });
        this.audioChunks = [];

        this.mediaRecorder.ondataavailable = (event) => {
          this.audioChunks.push(event.data);
        };

        this.mediaRecorder.start();
        this.isRecording = true;
      } catch (error) {
        console.error('Error accessing microphone:', error);
        this.$message.error('无法访问麦克风');
      }
    },

    async stopRecording() {
      if (!this.mediaRecorder || this.mediaRecorder.state === 'inactive') return;

      this.mediaRecorder.stop();
      this.isRecording = false;

      this.mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        const fileName = `recording_${Date.now()}.webm`;
        const formData = new FormData();
        formData.append('audio', audioBlob, fileName);

        try {
          const response = await axios.post('http://localhost:5000/api/interview', formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          });

          // 添加用户消息
          this.messages.push({
            type: 'user',
            text: response.data.user_text
          });
  
          // 添加AI消息
          const aiMessage = {
            type: 'ai',
            text: response.data.ai_response,
            audioUrl: response.data.ai_audio_url
          };
          this.messages.push(aiMessage);

          // 发送任务给数字人
          try {
            await this.$refs.digitalHuman.sendTask(response.data.ai_response);
          } catch (error) {
            console.error('Error sending task to digital human:', error);
            this.$message.warning('数字人响应失败，但语音正常播放');
          }

          this.$nextTick(() => {
            const container = this.$refs.messagesContainer;
            container.scrollTop = container.scrollHeight;
          });
        } catch (error) {
          console.error('Error sending audio:', error);
          this.$message.error('发送音频失败');
        }

        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
      };
    }
  }
}
</script>

<style scoped>
.interview-container {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: #6B2B63;
  padding-top: 60px;
  box-sizing: border-box;
  position: fixed;
  left: 0;
  top: 0;
}

.chat-layout {
  display: flex;
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
  background: #6B2B63;
  position: relative;
}

.interviewer-section {
  width: 780px;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0;
  background: rgba(0, 0, 0, 0.2);
  position: relative;
  overflow: hidden;
}

.chat-section {
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.95);
  margin: 0;
  padding: 0;
  overflow: hidden;
  position: relative;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: rgba(248, 250, 252, 0.98);
  margin: 0;
}

.message {
  margin-bottom: 25px;
  display: flex;
  flex-direction: column;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  align-items: flex-end;
}

.message.ai {
  align-items: flex-start;
}

.message-bubble {
  max-width: 70%;
  padding: 20px 25px;
  border-radius: 25px;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
  position: relative;
}

.user .message-bubble {
  background: linear-gradient(135deg, #8E44AD, #9B59B6);
  color: white;
  border-bottom-right-radius: 5px;
}

.ai .message-bubble {
  background: white;
  color: #333;
  border-bottom-left-radius: 5px;
}

.message-text {
  line-height: 1.6;
  font-size: 1.1em;
  margin-bottom: 8px;
}

.audio-player {
  margin-top: 10px;
  width: 100%;
}

.audio-player audio {
  width: 100%;
  height: 40px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.1);
}

.controls {
  padding: 20px;
  background: white;
  display: flex;
  justify-content: center;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.el-button {
  width: 200px;
  height: 50px;
  font-size: 1.1em;
  border-radius: 25px;
  transition: all 0.3s ease;
}

.el-button.recording {
  background: #E74C3C;
  border-color: #E74C3C;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

.el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.el-button:active {
  transform: translateY(1px);
}

.el-button i {
  margin-right: 8px;
  font-size: 1.2em;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-layout {
    flex-direction: column;
  }

  .interviewer-section {
    width: 100%;
    height: 300px;
  }

  .message-bubble {
    max-width: 85%;
  }
}
</style> 