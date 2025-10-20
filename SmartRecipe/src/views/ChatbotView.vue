<template>
  
      <!-- Chat Layout -->
      <v-container fluid class="pa-0 fill-height">
        <v-row no-gutters class="h-100">
          <!-- Sidebar (History) -->
          <v-col cols="2" class="grey lighten-3 pa-4">
            <div class="font-weight-medium">History</div>
          </v-col>

          <!-- Chat Area -->
          <v-col cols="10" class="pa-4 d-flex flex-column justify-end">
            <v-spacer></v-spacer>

            <!-- Chat Input -->
            <v-row align="center" no-gutters class="pa-2">
              <v-text-field
                v-model="message"
                placeholder="Type a message..."
                rounded
                hide-details
                dense
                filled
                class="flex-grow-1"
                append-inner-icon="mdi-magnify"
              ></v-text-field>

              <v-btn icon @click="sendMessage">
                <v-icon large>mdi-send</v-icon>
              </v-btn>
            </v-row>
          </v-col>
        </v-row>
      </v-container>
    
</template>

<script>
export default {
  name: 'ChatbotView',
  data() {
    return {
      message: ''
    }
  },
  methods: {
    sendMessage() {
      if (this.message.trim() !== '') {
        alert(`You said: ${this.message}`)
        this.message = ''
      }
    }
  }
}
</script>

<style scoped>
.fill-height {
  height: calc(100vh - 64px); /* Adjust if app-bar height changes */
}
</style>
