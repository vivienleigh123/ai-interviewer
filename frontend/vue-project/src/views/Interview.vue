<template>
  <div class="interview-container">
    <div class="chat-layout">
      <div class="interviewer-section">
        <img src="/images/interviewer.png" alt="AI面试官" class="interviewer-avatar" />
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

export default {
  name: 'Interview',
  data() {
    return {
      messages: [],
      isRecording: false,
      mediaRecorder: null,
      audioChunks: [],
    }
  },
  methods: {
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

          this.messages.push({
            type: 'user',
            text: response.data.user_text
          });

          this.messages.push({
            type: 'ai',
            text: response.data.ai_response,
            audioUrl: response.data.ai_audio_url
          });

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
  width: 380px;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0;
  background: rgba(0, 0, 0, 0.2);
  position: relative;
}

.interviewer-avatar {
  width: 100%;
  max-width: 380px;
  border-radius: 0;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  margin: 0;
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
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.el-button {
  width: 280px;
  height: 60px;
  font-size: 1.3em;
  border-radius: 30px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: linear-gradient(135deg, #8E44AD, #9B59B6);
  border: none;
  box-shadow: 0 4px 15px rgba(142, 68, 173, 0.3);
}

.el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(142, 68, 173, 0.4);
}

.recording {
  background: linear-gradient(135deg, #E74C3C, #C0392B) !important;
  box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3) !important;
  animation: pulseRecord 1.5s infinite;
}

@keyframes pulseRecord {
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

/* Custom scrollbar */
.messages::-webkit-scrollbar {
  width: 8px;
}

.messages::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

.messages::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.messages::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

/* Responsive design */
@media (max-width: 1024px) {
  .chat-layout {
    flex-direction: column;
  }

  .interviewer-section {
    width: 100%;
    height: auto;
    padding: 0;
    flex-direction: row;
    justify-content: flex-start;
    background: rgba(0, 0, 0, 0.3);
  }

  .interviewer-avatar {
    width: 100px;
    height: 100px;
    object-fit: cover;
    margin: 10px;
    border-radius: 10px;
  }

  .chat-section {
    height: calc(100% - 120px);
  }
}

@media (max-width: 768px) {
  .interview-container {
    padding-top: 50px;
  }

  .interviewer-section {
    padding: 0;
    height: 80px;
    background: rgba(0, 0, 0, 0.4);
  }

  .interviewer-avatar {
    width: 60px;
    height: 60px;
    margin: 10px;
  }

  .chat-section {
    height: calc(100% - 80px);
  }

  .message-bubble {
    max-width: 85%;
    padding: 15px 20px;
  }

  .controls {
    padding: 10px;
  }

  .el-button {
    width: 240px;
    height: 50px;
    font-size: 1.2em;
  }
}
</style> 