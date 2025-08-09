<template>
  <v-app>
    <v-main class="d-flex justify-center align-center" style="min-height: 100vh; background-color: #1c1c1c;">
      <v-card class="pa-6" width="400">
        <v-row align="center" justify="space-between">
          <v-avatar color="grey lighten-2">
            <span>App</span>
          </v-avatar>
          <v-card-title class="text-h6">Recipe Manager</v-card-title>
          <v-btn variant="outlined" size="small">Sign Up</v-btn>
        </v-row>

        <v-card-text>
          <v-icon class="mb-4" size="40">mdi-account</v-icon>

          <v-text-field
            v-model="email"
            label="Enter Email"
            prepend-inner-icon="mdi-email"
            type="email"
            variant="outlined"
            dense
          ></v-text-field>

          <v-text-field
            v-model="password"
            label="Password"
            prepend-inner-icon="mdi-lock"
            type="password"
            variant="outlined"
            dense
          ></v-text-field>

          <div class="text-right text-caption mb-4" style="cursor: pointer;">
            Forgot Password?
          </div>

          <v-btn
            color="primary"
            block
            rounded
            @click="login"
          >
            Sign In
          </v-btn>
        </v-card-text>
        <p v-if="errorMsg">{{ errorMsg }}</p>
      </v-card>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
import { signInWithEmailAndPassword, createUserWithEmailAndPassword  } from 'firebase/auth'
import { auth } from '@/firebase'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const email = ref('')
const password = ref('')
const errorMsg = ref('')
const router = useRouter()

const login = async () => {
  try {
    await signInWithEmailAndPassword(auth, email.value, password.value)
    router.push('/dashboard')
  } catch (error) {
    errorMsg.value = error.message
  }
}
const signup = async () => {
  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email.value, password.value)
    const user = userCredential.user
    const token = await user.getIdToken()

    // Call FastAPI to store user info
    const response = await fetch('http://localhost:8000/signup', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name: email.value.split('@')[0] }) // Optional custom name
    })

    const result = await response.json()

    if (response.ok) {
      router.push('/dashboard')
    } else {
      errorMsg.value = result.detail || 'Signup failed.'
    }
  } catch (error) {
    errorMsg.value = error.message
  }
}
</script>
