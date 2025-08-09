// src/stores/auth.js
import { defineStore } from 'pinia'
import { auth } from '../firebase'
import { onAuthStateChanged, signOut } from 'firebase/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    loading: true,
  }),

  actions: {
    init() {
      onAuthStateChanged(auth, (firebaseUser) => {
        this.user = firebaseUser
        this.loading = false
      })
    },

    logout() {
      signOut(auth)
    }
  },

  getters: {
    isAuthenticated: (state) => !!state.user,
  }
})
