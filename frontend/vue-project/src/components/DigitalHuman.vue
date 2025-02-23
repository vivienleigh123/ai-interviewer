<template>
  <div class="digital-human-container">
    <video ref="videoElement" autoplay playsinline class="digital-human-video"></video>
  </div>
</template>

<script>
export default {
  name: 'DigitalHuman',
  data() {
    return {
      sessionId: null,
      peerConnection: null,
      videoElement: null,
      apiKey: import.meta.env.VITE_HEYGEN_API_KEY,
      isSessionActive: false
    };
  },
  async mounted() {
    this.videoElement = this.$refs.videoElement;
    await this.initializeSession();
  },
  beforeUnmount() {
    this.closeSession();
  },
  methods: {
    async initializeSession() {
      try {
        // 1. 创建新会话
        const sessionResponse = await fetch('https://api.heygen.com/v1/streaming.new', {
          method: 'POST',
          headers: {
            'accept': 'application/json',
            'content-type': 'application/json',
            'x-api-key': this.apiKey
          },
          body: JSON.stringify({
            quality: 'high',
            avatar_id: 'ef08039a41354ed5a20565db899373f3',
            voice_id: 'c564e4fb7dbb4ce0a9b75d3966b2f4e9',
            voice: {
              rate: 1 
            },
            video_encoding: 'VP8',
            disable_idle_timeout: false
          })
        }); 

        const sessionData = await sessionResponse.json();
        if (sessionData.code !== 100) {
          throw new Error('创建会话失败');
        }

        this.sessionId = sessionData.data.session_id;
        const { sdp, ice_servers2, session_id } = sessionData.data;
        console.log(sdp, ice_servers2, session_id);

        // 2. 设置 WebRTC 对等连接
        this.peerConnection = new RTCPeerConnection({ iceServers: ice_servers2 });

        // 处理传入的轨道
        this.peerConnection.ontrack = (event) => {
          if (this.videoElement) {
            this.videoElement.srcObject = event.streams[0];
            console.log('接收到视频流');
          }
        };

        // 处理 ICE 候选
        this.peerConnection.onicecandidate = async ({ candidate }) => {
          if (candidate) {
            console.log('发送 ICE 候选:', candidate);
            try {
              await fetch('https://api.heygen.com/v1/streaming.ice', {
                method: 'POST',
                headers: {
                  'accept': 'application/json',
                  'content-type': 'application/json',
                  'x-api-key': this.apiKey
                },
                body: JSON.stringify({
                  session_id: this.sessionId,
                  candidate: {
                    candidate: candidate.candidate,
                    sdpMid: candidate.sdpMid,
                    sdpMLineIndex: candidate.sdpMLineIndex
                  }
                })
              });
            } catch (error) {
              console.error('发送 ICE 候选时出错:', error);
            }
          }
        };

        // 设置远程描述
        await this.peerConnection.setRemoteDescription(new RTCSessionDescription({
          type: 'offer',
          sdp: sdp.sdp
        }));

        // 创建并设置本地描述
        const answer = await this.peerConnection.createAnswer();
        await this.peerConnection.setLocalDescription(answer);
        console.log('本地描述已设置');

        // 3. 启动会话
        const startResponse = await fetch('https://api.heygen.com/v1/streaming.start', {
          method: 'POST',
          headers: {
            'accept': 'application/json',
            'content-type': 'application/json',
            'x-api-key': this.apiKey
          },
          body: JSON.stringify({
            session_id: this.sessionId,
            sdp: {
              type: 'answer',
              sdp: answer.sdp
            }
          })
        });

        const startData = await startResponse.json();
        console.log('启动会话响应:', startData);
        if (startData.message === 'success') {
          this.isSessionActive = true;
          this.$emit('session-ready');
        }
      } catch (error) {
        console.error('Error initializing digital human:', error);
        this.$emit('session-error', error);
      }
    },

    async sendTask(text) {
      if (!this.isSessionActive || !this.sessionId) {
        throw new Error('Session not active');
      }

      try {
        const response = await fetch('https://api.heygen.com/v1/streaming.task', {
          method: 'POST',
          headers: {
            'accept': 'application/json',
            'content-type': 'application/json',
            'x-api-key': this.apiKey
          },
          body: JSON.stringify({
            session_id: this.sessionId,
            text: text
          })
        });

        const data = await response.json();
        return data;
      } catch (error) {
        console.error('Error sending task:', error);
        throw error;
      }
    },


    async closeSession() {
      if (this.sessionId) {
        try {
          await fetch('https://api.heygen.com/v1/streaming.stop', {
            method: 'POST',
            headers: {
              'accept': 'application/json',
              'content-type': 'application/json',
              'x-api-key': this.apiKey
            },
            body: JSON.stringify({
              session_id: this.sessionId
            })
          });
        } catch (error) {
          console.error('Error closing session:', error);
        }
      }

      if (this.peerConnection) {
        this.peerConnection.close();
        this.peerConnection = null;
      }

      if (this.videoElement && this.videoElement.srcObject) {
        this.videoElement.srcObject.getTracks().forEach(track => track.stop());
        this.videoElement.srcObject = null;
      }

      this.sessionId = null;
      this.isSessionActive = false;
    }
  }
}
</script>

<style scoped>
.digital-human-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: transparent;
}

.digital-human-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  background: transparent;
}
</style>
