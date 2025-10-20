// src/stores/auth.js
import { defineStore } from 'pinia'
import { useRouter } from 'vue-router' // Import useRouter

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('authToken') || null, // Load token from localStorage on init
    loading: false, // No longer waiting for Firebase, set to false initially or manage during API calls
    error: null, // To store potential auth errors
  }),

  actions: {
    // Action to set the token in state and localStorage
    setToken(newToken) {
      this.token = newToken
      if (newToken) {
        localStorage.setItem('authToken', newToken)
      } else {
        localStorage.removeItem('authToken')
      }
      this.error = null // Clear errors on successful token set/clear
    },

    // Action to clear the token (logout)
    clearToken() {
      this.setToken(null)
      // No need to explicitly use router here if handled in component/guard
    },

    // Action called during login/OTP verification
    async loginWithOtp(phone_number, otp_code) {
      this.loading = true
      this.error = null
      const router = useRouter() // Get router instance inside action if needed for redirect
      try {
        const response = await fetch('http://127.0.0.1:8000/verify-otp-and-login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ phone_number, otp_code }),
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || 'OTP verification failed.')
        }

        const data = await response.json()
        this.setToken(data.access_token)
        // Redirect on successful login - handled in LoginView now
        // router.push('/') // Or '/recipes'

      } catch (err) {
        console.error('Login Error:', err)
        this.error = err.message || 'An error occurred during login.'
        this.setToken(null) // Ensure token is cleared on error
      } finally {
        this.loading = false
      }
    },

     // Action to handle user signup
     async registerUser(userData) {
      this.loading = true;
      this.error = null;
      try {
        const response = await fetch('http://127.0.0.1:8000/signUp', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(userData), // { user_name, phone_number, full_name?, email? }
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Sign up failed.');
        }

        // Optionally, automatically request OTP or prompt user to log in after signup
        console.log("Signup successful, user created:", await response.json());
        // You might want to automatically trigger OTP request here or just inform the user

      } catch (err) {
        console.error('Signup Error:', err);
        this.error = err.message || 'An error occurred during signup.';
      } finally {
        this.loading = false;
      }
    },

    // Action for requesting OTP
    async requestOtpCode(phone_number) {
      this.loading = true;
      this.error = null;
      try {
        const response = await fetch('http://127.0.0.1:8000/send-login-otp', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ phone_number }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to send OTP.');
        }

        console.log("OTP request successful:", await response.json());
        // UI should now show the OTP input field

      } catch (err) {
        console.error('Request OTP Error:', err);
        this.error = err.message || 'An error occurred while requesting OTP.';
      } finally {
        this.loading = false;
      }
    },


    // Action called when app loads to check localStorage
    initializeAuth() {
       // Token is already loaded from localStorage in the state definition
      this.loading = false; // Set loading to false immediately
      console.log("Auth initialized, token from storage:", this.token);
    },

    // Combined logout action
    logout() {
      this.clearToken();
      // Redirect is handled by the navigation guard or component
      // const router = useRouter(); // Cannot use useRouter directly here
      // router.push('/login'); // This won't work reliably here, do it in component/guard
    }
  },

  getters: {
    // Check if token exists
    isAuthenticated: (state) => !!state.token,
    // Getter to expose loading state
    isLoading: (state) => state.loading,
    // Getter to expose error state
    authError: (state) => state.error,
  }
})