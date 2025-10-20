<template>
  <v-container fluid class="fill-height pa-0 d-flex flex-column">
    
    <v-col
      ref="chatContainer"
      class="flex-grow-1 overflow-y-auto pa-4"
      style="height: 0px;"
    >
      <div v-for="msg in messages" :key="msg.id" :class="['d-flex mb-4', msg.from === 'user' ? 'justify-end' : 'justify-start']">
        <v-chip
          :color="msg.from === 'user' ? 'primary' : 'grey lighten-1'"
          :class="['pa-3', msg.isError ? 'error' : '']"
          style="max-width: 70%; white-space: pre-wrap; height: auto;"
        >
          {{ msg.text }}
        </v-chip>
      </div>
       <v-skeleton-loader
          v-if="loading"
          type="list-item"
          width="150"
          class="mb-4"
        ></v-skeleton-loader>
    </v-col>

    <v-col class="flex-grow-0 pa-4">
      <v-row align="center" no-gutters>
        <v-text-field
          v-model="message"
          @keydown.enter="sendMessage"
          placeholder="Type a message..."
          rounded
          hide-details
          dense
          filled
          class="flex-grow-1"
          :disabled="loading"
        ></v-text-field>

        <v-btn icon @click="sendMessage" :loading="loading" :disabled="loading" class="ml-2">
          <v-icon large>mdi-send</v-icon>
        </v-btn>
      </v-row>
    </v-col>

  </v-container>
</template>

<script>
import { useAuthStore } from '../stores/auth';

export default {
  name: 'ChatbotView',
  data() {
    return {
      message: '', // The user's current typed message
      loading: false, // True when waiting for the bot
      messages: [] // The list of all chat messages
    }
  },
  mounted() {
    // Add an initial greeting message from the bot
    this.messages.push({
      id: Date.now(),
      text: 'Hello! You can ask me for recipe ideas, substitutes, or seasonal suggestions.',
      from: 'bot',
      isError: false
    });
  },
  methods: {
    // Scrolls the chat window to the bottom
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

      // 1. Add user's message to the UI
      this.messages.push({
        id: Date.now(),
        text: userMessageText,
        from: 'user',
        isError: false
      });
      
      this.message = ''; // Clear the input field
      this.loading = true;
      this.scrollToBottom();

      const authStore = useAuthStore();
      const token = authStore.token;

      // Check for auth token
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
        // 2. Send the message to the new backend endpoint
        const response = await fetch('http://127.0.0.1:8000/chatbot/query', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ query: userMessageText })
        });

        // Handle auth errors
        if (response.status === 401) {
          authStore.logout();
          this.$router.push('/login');
          throw new Error('Unauthorized. Please log in.');
        }
        if (!response.ok) {
          throw new Error('The server had trouble responding.');
        }

        const data = await response.json();
        
        // 3. Add the bot's response to the UI
        this.messages.push({
          id: Date.now(),
          text: data.response, // 'response' field from our Pydantic model
          from: 'bot',
          isError: false
        });

      } catch (err) {
        // Handle any errors
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
.fill-height {
  height: calc(100vh - 64px); /* Adjust 64px if your app bar height is different */
}
</style>