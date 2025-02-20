<template>
  <div class="history-container">
    <el-card class="history-box">
      <template #header>
        <div class="header">
          <h2>面试历史记录</h2>
          <div class="header-subtitle">您的每一次面试都是宝贵的经验</div>
        </div>
      </template>
      <el-timeline>
        <el-timeline-item
          v-for="interview in interviews"
          :key="interview.id"
          :timestamp="formatDate(interview.created_at)"
          placement="top"
          type="primary"
        >
          <el-card class="interview-card">
            <div class="interview-content">
              <div class="message user">
                <div class="avatar">
                  <i class="el-icon-user"></i>
                </div>
                <div class="message-content">
                  <div class="label">我的回答</div>
                  <div class="text">{{ interview.user_text }}</div>
                </div>
              </div>
              <div class="message ai">
                <div class="avatar">
                  <i class="el-icon-service"></i>
                </div>
                <div class="message-content">
                  <div class="label">面试官回复</div>
                  <div class="text">{{ interview.ai_response }}</div>
                  <div class="audio-player">
                    <audio :src="interview.ai_audio_url" controls></audio>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'History',
  data() {
    return {
      interviews: []
    }
  },
  methods: {
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    async fetchHistory() {
      try {
        const response = await axios.get('http://localhost:5000/api/history');
        this.interviews = response.data;
      } catch (error) {
        console.error('Error fetching history:', error);
        this.$message.error('获取历史记录失败');
      }
    }
  },
  mounted() {
    this.fetchHistory();
  }
}
</script>

<style scoped>
.history-container {
  width: 100%;
  min-height: calc(100vh - 60px);
  padding: 20px;
  display: flex;
  justify-content: center;
  background: linear-gradient(135deg, rgba(26, 42, 108, 0.8), rgba(178, 31, 31, 0.8), rgba(253, 187, 45, 0.8));
  background-size: 400% 400%;
  animation: gradientBG 15s ease infinite;
}

@keyframes gradientBG {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.history-box {
  width: 100%;
  max-width: 1000px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  border: none;
  margin-top: 20px;
}

.header {
  text-align: center;
  padding: 20px 0;
}

.header h2 {
  margin: 0;
  color: #333;
  font-size: 2em;
  font-weight: 600;
}

.header-subtitle {
  color: #666;
  margin-top: 10px;
  font-size: 1.1em;
}

.interview-card {
  margin-bottom: 30px;
  border-radius: 15px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
  border: none;
}

.interview-content {
  padding: 20px;
}

.message {
  display: flex;
  align-items: flex-start;
  margin-bottom: 25px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  flex-shrink: 0;
}

.user .avatar {
  background: linear-gradient(135deg, #007AFF, #00C6FF);
  color: white;
}

.ai .avatar {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
}

.avatar i {
  font-size: 1.5em;
}

.message-content {
  flex: 1;
}

.label {
  font-weight: 600;
  margin-bottom: 8px;
  font-size: 1.1em;
}

.user .label {
  color: #007AFF;
}

.ai .label {
  color: #4CAF50;
}

.text {
  line-height: 1.6;
  color: #333;
  background: #f8f9fa;
  padding: 15px 20px;
  border-radius: 15px;
  font-size: 1.1em;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.audio-player {
  margin-top: 15px;
}

.audio-player audio {
  width: 100%;
  height: 40px;
  border-radius: 10px;
}

/* Timeline customization */
:deep(.el-timeline-item__node--normal) {
  background-color: var(--el-color-primary);
  border-color: var(--el-color-primary);
}

:deep(.el-timeline-item__tail) {
  border-left-color: rgba(64, 158, 255, 0.2);
}

:deep(.el-timeline-item__timestamp) {
  color: #666;
  font-size: 1em;
  padding-top: 8px;
}

/* Responsive design */
@media (max-width: 768px) {
  .history-container {
    padding: 10px;
  }

  .message {
    flex-direction: column;
  }

  .avatar {
    margin-bottom: 10px;
  }

  .text {
    font-size: 1em;
    padding: 12px 15px;
  }
}
</style> 