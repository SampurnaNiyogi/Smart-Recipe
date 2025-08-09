<template>
  <v-app>
    <v-main>
      <v-container>
        <!-- Profile Card -->
        <v-card class="pa-8 mt-12 mx-auto" max-width="500" outlined>
          <div class="text-center mb-6">
            <v-icon size="60">mdi-account</v-icon>
          </div>

          <v-text-field
            v-model="user.username"
            label="Username"
            prepend-inner-icon="mdi-account"
          />
          <v-text-field
            v-model="user.email"
            label="Email"
            prepend-inner-icon="mdi-email"
          />
          <v-text-field
            v-model="user.password"
            label="Password"
            type="password"
            prepend-inner-icon="mdi-lock"
          />

          <div class="text-right mt-2">
            <v-btn text color="primary" @click="changePassword">
              Change password
            </v-btn>
          </div>
        </v-card>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: 'ProfileView',
  data() {
    return {
      user: {
        username: '',
        email: '',
        password: ''
      }
    }
  },
  methods: {
    changePassword() {
      alert('Password change logic triggered.')
    }
  }
}
</script>
