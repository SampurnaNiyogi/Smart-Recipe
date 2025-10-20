<template>
  <v-app>
    <v-main class="d-flex justify-center align-center" style="min-height: 100vh; background-color: #e0f2f7;"> 
      <v-card class="pa-6" width="450" elevation="5"> 

        <v-tabs v-model="tab" grow background-color="teal darken-1" dark>
          <v-tab value="login">Sign In</v-tab>
          <v-tab value="signup">Sign Up</v-tab>
        </v-tabs>

        <v-card-text>
           <v-window v-model="tab">
            <v-window-item value="login">
              <v-form @submit.prevent="handleLoginSubmit">
                <v-icon class="mb-4" size="40" color="teal">mdi-login-variant</v-icon>
                <h3 class="text-center mb-4 text-teal">Sign In</h3>

                <v-text-field
                  v-model="loginPhoneNumber"
                  label="Phone Number"
                  prepend-inner-icon="mdi-phone"
                  placeholder="+91XXXXXXXXXX"
                  variant="outlined"
                  dense
                  :rules="[rules.required, rules.phone]"
                  class="mb-3"
                  :disabled="otpSent"
                ></v-text-field>

                <v-btn
                  color="teal darken-2"
                  block
                  rounded
                  @click="requestOtp"
                  :loading="authStore.isLoading && !otpSent"
                  :disabled="otpSent || !isPhoneValid(loginPhoneNumber)"
                  v-if="!otpSent"
                  class="mb-3"
                >
                  Send OTP
                </v-btn>

                <v-text-field
                  v-if="otpSent"
                  v-model="otpCode"
                  label="OTP Code"
                  prepend-inner-icon="mdi-numeric"
                  type="number"
                  variant="outlined"
                  dense
                  :rules="[rules.required, rules.otp]"
                  class="mb-3"
                  maxlength="6"
                ></v-text-field>

                 <v-btn
                  v-if="otpSent"
                  color="teal darken-3"
                  block
                  rounded
                  type="submit"
                  :loading="authStore.isLoading && otpSent"
                  :disabled="!otpCode || otpCode.length !== 6"
                >
                  Verify OTP & Sign In
                </v-btn>

                <div v-if="otpSent" class="text-center mt-2">
                   <v-btn variant="text" size="small" @click="resetLogin" color="grey">Change Number / Resend</v-btn>
                </div>

                </v-form>
            </v-window-item>

            <v-window-item value="signup">
               <v-form @submit.prevent="handleSignupSubmit">
                <v-icon class="mb-4" size="40" color="indigo">mdi-account-plus</v-icon>
                 <h3 class="text-center mb-4 text-indigo">Create Account</h3>

                <v-text-field
                  v-model="signupUsername"
                  label="Username"
                  prepend-inner-icon="mdi-account"
                  variant="outlined"
                  dense
                  :rules="[rules.required, rules.minLength(3)]"
                  class="mb-3"
                ></v-text-field>

                <v-text-field
                  v-model="signupPhoneNumber"
                  label="Phone Number"
                  prepend-inner-icon="mdi-phone"
                  placeholder="+91XXXXXXXXXX"
                  variant="outlined"
                  dense
                  :rules="[rules.required, rules.phone]"
                  class="mb-3"
                ></v-text-field>

                 <v-text-field
                  v-model="signupFullName"
                  label="Full Name (Optional)"
                  prepend-inner-icon="mdi-card-account-details"
                  variant="outlined"
                  dense
                  class="mb-3"
                ></v-text-field>

                 <v-text-field
                  v-model="signupEmail"
                  label="Email (Optional)"
                  prepend-inner-icon="mdi-email"
                  type="email"
                  variant="outlined"
                  dense
                  :rules="[rules.email]"
                  class="mb-3"
                ></v-text-field>

                <v-btn
                  color="indigo darken-1"
                  block
                  rounded
                  type="submit"
                  :loading="authStore.isLoading"
                >
                  Sign Up
                </v-btn>
              </v-form>
            </v-window-item>
          </v-window>
        </v-card-text>

        <v-alert v-if="authStore.authError" type="error" dense class="mt-4">
          {{ authStore.authError }}
        </v-alert>
         <v-alert v-if="signupSuccessMessage" type="success" dense class="mt-4">
          {{ signupSuccessMessage }}
        </v-alert>

      </v-card>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

// --- State ---
const tab = ref('login') // 'login' or 'signup'

// Login State
const loginPhoneNumber = ref('')
const otpCode = ref('')
const otpSent = ref(false)

// Signup State
const signupUsername = ref('')
const signupPhoneNumber = ref('')
const signupFullName = ref('')
const signupEmail = ref('')
const signupSuccessMessage = ref('')


// --- Validation Rules ---
const rules = {
  required: value => !!value || 'Required.',
  phone: value => {
    const pattern = /^\+?[1-9]\d{1,14}$/ // Basic E.164 format check
    return pattern.test(value) || 'Invalid phone number format (e.g., +919876543210).'
  },
   otp: value => (value && value.length === 6 && /^\d+$/.test(value)) || 'OTP must be 6 digits.',
   email: value => {
     if (!value) return true // Optional
     const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
     return pattern.test(value) || 'Invalid e-mail.'
   },
   minLength: (length) => value => (value && value.length >= length) || `Min ${length} characters`,
}

// --- Computed ---
const isPhoneValid = (phone) => /^\+?[1-9]\d{1,14}$/.test(phone);

// --- Methods ---
const requestOtp = async () => {
  if (!isPhoneValid(loginPhoneNumber.value)) {
     authStore.error = 'Please enter a valid phone number.'; // Use store error for consistency
    return;
  }
  await authStore.requestOtpCode(loginPhoneNumber.value);
  if (!authStore.authError) { // Check if the request was successful
      otpSent.value = true;
  }
}

const handleLoginSubmit = async () => {
  if (!loginPhoneNumber.value || !otpCode.value || otpCode.value.length !== 6) {
     authStore.error = 'Please enter phone number and valid 6-digit OTP.';
     return;
  }
  await authStore.loginWithOtp(loginPhoneNumber.value, otpCode.value);
   if (authStore.isAuthenticated) {
    router.push('/'); // Redirect to home or dashboard after login
  }
}

const resetLogin = () => {
  otpSent.value = false;
  otpCode.value = '';
  // Keep loginPhoneNumber.value as is, or clear it:
  // loginPhoneNumber.value = '';
  authStore.error = null; // Clear previous errors
}


const handleSignupSubmit = async () => {
  // Add validation checks if needed using rules
  const userData = {
    user_name: signupUsername.value,
    phone_number: signupPhoneNumber.value,
    full_name: signupFullName.value || null, // Send null if empty
    email: signupEmail.value || null,       // Send null if empty
  };

  // Basic frontend validation (you can enhance this)
  if (!userData.user_name || !userData.phone_number || !isPhoneValid(userData.phone_number)) {
     authStore.error = 'Username and valid phone number are required for signup.';
     return;
  }
   if (userData.email && !rules.email(userData.email)) {
     authStore.error = 'Please enter a valid email address or leave it empty.';
     return;
   }


  await authStore.registerUser(userData);

  if (!authStore.authError) {
      signupSuccessMessage.value = 'Account created successfully! Please go to Sign In to request OTP and log in.';
      // Optionally reset form fields
      signupUsername.value = '';
      signupPhoneNumber.value = '';
      signupFullName.value = '';
      signupEmail.value = '';
      // Maybe switch tab?
      // tab.value = 'login';
    } else {
       signupSuccessMessage.value = ''; // Clear success message on error
    }
}

</script>

<style scoped>
/* Optional: Add custom styles */
.text-teal {
  color: #00695C; /* teal darken-3 */
}
.text-indigo {
   color: #303F9F; /* indigo darken-1 */
}
</style>