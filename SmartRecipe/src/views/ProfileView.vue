<template>
  <v-container>
    <v-card class="pa-8 mt-12 mx-auto rounded-lg" max-width="600" elevation="4" :loading="loading">
      <div class="d-flex flex-column align-center mb-6">
        <v-avatar color="teal" size="80" class="mb-4">
          <span class="text-h4 text-white">{{ user.user_name.charAt(0).toUpperCase() }}</span>
        </v-avatar>
        <v-card-title class="text-h5 font-weight-bold pa-0">User Profile</v-card-title>
      </div>

      <v-alert v-if="error" type="error" variant="tonal" class="mb-4">{{ error }}</v-alert>
      <v-alert v-if="successMsg" type="success" variant="tonal" class="mb-4">{{ successMsg }}</v-alert>

      <v-form @submit.prevent="saveProfile">
        <v-text-field
          v-model="editForm.user_name"
          label="Username"
          prepend-inner-icon="mdi-account"
          :readonly="!isEditing"
          :variant="isEditing ? 'outlined' : 'filled'"
          class="mb-3"
          :color="isEditing ? 'teal' : ''"
        />
        
        <v-text-field
          v-model="user.phone_number"
          label="Phone Number"
          prepend-inner-icon="mdi-phone"
          readonly
          variant="filled"
          class="mb-3"
          hint="Phone number cannot be changed"
          persistent-hint
        />
        
        <v-text-field
          v-model="editForm.full_name"
          label="Full Name"
          prepend-inner-icon="mdi-card-account-details"
          :readonly="!isEditing"
          :variant="isEditing ? 'outlined' : 'filled'"
          class="mb-3"
          :color="isEditing ? 'teal' : ''"
        />
        
        <v-text-field
          v-model="editForm.email"
          label="Email"
          prepend-inner-icon="mdi-email"
          :readonly="!isEditing"
          :variant="isEditing ? 'outlined' : 'filled'"
          class="mb-3"
          :color="isEditing ? 'teal' : ''"
        />

        <div class="d-flex justify-end mt-4">
          <v-btn 
            v-if="!isEditing" 
            color="teal" 
            prepend-icon="mdi-pencil" 
            @click="enableEdit"
          >
            Edit Profile
          </v-btn>
          
          <template v-else>
            <v-btn 
              variant="text" 
              color="grey-darken-1" 
              class="mr-3" 
              @click="cancelEdit"
              :disabled="saving"
            >
              Cancel
            </v-btn>
            <v-btn 
              color="teal-darken-2" 
              type="submit" 
              prepend-icon="mdi-content-save"
              :loading="saving"
            >
              Save Changes
            </v-btn>
          </template>
        </div>
      </v-form>
    </v-card>
  </v-container>
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
      editForm: {
        user_name: '',
        email: '',
        full_name: ''
      },
      isEditing: false,
      loading: false,
      saving: false,
      error: null,
      successMsg: null
    }
  },
  async mounted() {
    await this.fetchUserProfile();
  },
  methods: {
    async fetchUserProfile() {
      const authStore = useAuthStore();
      const token = authStore.token;
      this.error = null;

      if (!token) {
        this.$router.push('/login');
        return;
      }

      this.loading = true;
      try {
        const response = await fetch("http://127.0.0.1:8000/users/me", {
          headers: { "Authorization": `Bearer ${token}` }
        });

        if (response.status === 401 || response.status === 403) {
           authStore.logout();
           this.$router.push('/login');
           return;
        }

        if (!response.ok) throw new Error("Failed to fetch profile");

        const userData = await response.json();
        this.user = { ...userData };
        this.resetEditForm();

      } catch (err) {
         this.error = err.message;
      } finally {
        this.loading = false;
      }
    },
    enableEdit() {
      this.successMsg = null;
      this.error = null;
      this.resetEditForm();
      this.isEditing = true;
    },
    cancelEdit() {
      this.isEditing = false;
      this.resetEditForm();
      this.error = null;
    },
    resetEditForm() {
      this.editForm = {
        user_name: this.user.user_name,
        email: this.user.email || '',
        full_name: this.user.full_name || ''
      };
    },
    async saveProfile() {
      const authStore = useAuthStore();
      this.saving = true;
      this.error = null;
      this.successMsg = null;

      try {
        const response = await fetch("http://127.0.0.1:8000/users/me", {
          method: "PUT",
          headers: {
            "Authorization": `Bearer ${authStore.token}`,
            "Content-Type": "application/json"
          },
          body: JSON.stringify(this.editForm)
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || "Failed to update profile");
        }

        const updatedData = await response.json();
        this.user = { ...updatedData };
        this.isEditing = false;
        this.successMsg = "Profile updated successfully!";
      } catch (err) {
        this.error = err.message;
      } finally {
        this.saving = false;
      }
    }
  }
}
</script>