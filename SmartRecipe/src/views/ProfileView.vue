<template>
  <v-app>
    <v-main>
      <v-container>
        <!-- Profile Card -->
        <v-card class="pa-8 mt-12 mx-auto" max-width="500" outlined :loading="loading">
          <v-card-title class="text-center mb-6">User Profile</v-card-title>

          <v-alert v-if="error" type="error" dense class="mb-4">{{ error }}</v-alert>

          <v-text-field
            v-model="user.user_name"
            label="Username"
            prepend-inner-icon="mdi-account"
            readonly
            variant="filled"
            class="mb-3"
          />
           <v-text-field
            v-model="user.phone_number"
            label="Phone Number"
            prepend-inner-icon="mdi-phone"
            readonly
            variant="filled"
            class="mb-3"
          />
          <v-text-field
            v-model="user.full_name"
            label="Full Name"
            prepend-inner-icon="mdi-card-account-details"
            readonly
            variant="filled"
            class="mb-3"
             hint="Not set"
             :persistent-hint="!user.full_name"
          />
          <v-text-field
            v-model="user.email"
            label="Email"
            prepend-inner-icon="mdi-email"
            readonly
            variant="filled"
            class="mb-3"
            hint="Not set"
            :persistent-hint="!user.email"
          />

        </v-card>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { useAuthStore } from '../stores/auth';
export default {
  name: 'ProfileView',
  data() {
    return {
      user: {
        user_name: '', 
        email: '',
        phone_number: '',
        full_name: ''
      },
      loading: false,
      error: null
    }
  },
  async mounted() {
    await this.fetchUserProfile(); // Fetch data when component is ready
  },
  methods: {
    async fetchUserProfile() {
      const authStore = useAuthStore();
      const token = authStore.token;
      this.error = null; // Clear previous errors

      if (!token) {
        this.error = "Not logged in.";
        alert(this.error);
        this.$router.push('/login');
        return;
      }

      this.loading = true;
      try {
        const response = await fetch("http://127.0.0.1:8000/users/me", {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        });

        if (response.status === 401 || response.status === 403) {
           alert("Authentication failed. Please log in again.");
           authStore.logout();
           this.$router.push('/login');
           throw new Error('Unauthorized');
        }

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || `Failed to fetch profile (${response.status})`);
        }

        const userData = await response.json();
        // Map backend fields to frontend data properties
        this.user.user_name = userData.user_name;
        this.user.email = userData.email || ''; // Handle potential null email
        this.user.phone_number = userData.phone_number;
        this.user.full_name = userData.full_name || ''; // Handle potential null full name
        // this.user.uuid = userData.uuid;

      } catch (err) {
         if (err.message !== 'Unauthorized') {
             console.error("Failed to fetch user profile:", err);
             this.error = err.message;
             alert(`Error loading profile: ${this.error}`);
         }
      } finally {
        this.loading = false;
      }
    },
  }
}
</script>
