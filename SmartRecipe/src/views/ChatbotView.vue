<template>
  <v-container class="fill-height pa-4 d-flex flex-column align-center justify-center bg-grey-lighten-4" fluid>
    <v-card class="d-flex flex-column rounded-xl overflow-hidden elevation-6" width="100%" max-width="800" height="85vh">
      
      <v-toolbar color="teal-darken-3" class="px-2" elevation="2">
        <v-avatar color="white" size="40" class="mr-3">
          <v-icon color="teal" size="24">mdi-robot-outline</v-icon>
        </v-avatar>
        <v-toolbar-title class="font-weight-bold text-white">Sous Chef AI</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn icon color="white" @click="$router.push('/')">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-toolbar>

      <div ref="chatContainer" class="flex-grow-1 overflow-y-auto pa-4 bg-white" style="scroll-behavior: smooth;">
        <div v-for="msg in messages" :key="msg.id" :class="['d-flex mb-6', msg.from === 'user' ? 'justify-end' : 'justify-start']">
          
          <v-avatar v-if="msg.from === 'bot'" color="teal-lighten-5" size="36" class="mr-2 mt-auto mb-auto border">
            <v-icon color="teal" size="20">mdi-robot</v-icon>
          </v-avatar>

          <v-card
            :color="msg.from === 'user' ? 'teal-darken-1' : 'grey-lighten-4'"
            :class="[
              'pa-3', 
              msg.from === 'user' ? 'text-white rounded-ts-xl rounded-te-xl rounded-bs-xl rounded-be-0' : 'text-grey-darken-4 rounded-ts-xl rounded-te-xl rounded-be-xl rounded-bs-0'
            ]"
            :elevation="msg.from === 'user' ? 2 : 0"
            max-width="75%"
            style="line-height: 1.5;"
          >
            <div style="white-space: pre-wrap; word-break: break-word;">{{ msg.text }}</div>
          </v-card>

          <v-avatar v-if="msg.from === 'user'" color="teal-darken-3" size="36" class="ml-2 mt-auto mb-auto">
            <v-icon color="white" size="20">mdi-account</v-icon>
          </v-avatar>
        </div>

        <div v-if="loading" class="d-flex justify-start mb-6">
          <v-avatar color="teal-lighten-5" size="36" class="mr-2 mt-auto mb-auto border">
            <v-icon color="teal" size="20">mdi-robot</v-icon>
          </v-avatar>
          <v-card color="grey-lighten-4" class="pa-4 rounded-ts-xl rounded-te-xl rounded-be-xl rounded-bs-0" elevation="0">
            <div class="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </v-card>
        </div>
      </div>

      <v-divider></v-divider>

      <div class="pa-4 bg-grey-lighten-5">
        <v-text-field
          v-model="message"
          @keydown.enter="sendMessage"
          placeholder="Ask me for a recipe, substitute, or seasonal dish..."
          variant="outlined"
          bg-color="white"
          hide-details
          rounded="pill"
          color="teal"
          density="comfortable"
          :disabled="loading"
        >
          <template v-slot:append-inner>
            <v-btn 
              icon="mdi-send" 
              color="teal" 
              variant="flat" 
              size="small" 
              class="mr-n1"
              @click="sendMessage" 
              :loading="loading" 
              :disabled="loading || !message.trim()"
            ></v-btn>
          </template>
        </v-text-field>
      </div>
    </v-card>
  </v-container>
</template>

<script>
import { useAuthStore } from '../stores/auth';

export default {
  name: 'ChatbotView',
  data() {
    return {
      message: '',
      loading: false,
      messages: []
    }
  },
  mounted() {
    this.messages.push({
      id: Date.now(),
      text: 'Hello! I am your AI Sous Chef. You can ask me for recipe ideas, ingredient substitutes, or seasonal suggestions.',
      from: 'bot',
      isError: false
    });
  },
  methods: {
    scrollToBottom() {
       this.$nextTick(() => {
          const container = this.$refs.chatContainer;
          if (container) {
            container.scrollTop = container.scrollHeight;
          }
        });
    },
    async sendMessage() {
      const userMessageText = this.message.trim();
      if (userMessageText === '' || this.loading) return;

      this.messages.push({
        id: Date.now(),
        text: userMessageText,
        from: 'user',
        isError: false
      });
      
      this.message = '';
      this.loading = true;
      this.scrollToBottom();

      const authStore = useAuthStore();
      const token = authStore.token;

      if (!token) {
        this.messages.push({
          id: Date.now(),
          text: 'Authentication error. Please log in again to use the chatbot.',
          from: 'bot',
          isError: true
        });
        this.loading = false;
        this.scrollToBottom();
        authStore.logout();
        this.$router.push('/login');
        return;
      }

      try {
        const response = await fetch('http://127.0.0.1:8000/chatbot/query', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ query: userMessageText })
        });

        if (response.status === 401) {
          authStore.logout();
          this.$router.push('/login');
          return;
        }
        if (!response.ok) throw new Error('The server had trouble responding.');

        const data = await response.json();
        
        this.messages.push({
          id: Date.now(),
          text: data.response,
          from: 'bot',
          isError: false
        });

      } catch (err) {
        this.messages.push({
          id: Date.now(),
          text: `Sorry, an error occurred: ${err.message}`,
          from: 'bot',
          isError: true
        });
      } finally {
        this.loading = false;
        this.scrollToBottom();
      }
    }
  }
}
</script>

<style scoped>
.typing-indicator span {
  display: inline-block;
  width: 6px;
  height: 6px;
  background-color: #00897B;
  border-radius: 50%;
  margin: 0 2px;
  animation: typing 1.4s infinite both;
}
.typing-indicator span:nth-child(1) { animation-delay: 0s; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}
</style>