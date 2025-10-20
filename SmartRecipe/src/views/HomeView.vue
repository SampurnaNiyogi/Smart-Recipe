<template>
  <v-app>
    <v-main>
      <v-container>
        <v-row class="mt-10">
          <v-col>
             <h2>Hi {{ userGreetingName }}!</h2>
            <p>Welcome to your personal recipe manager.....</p>
          </v-col>
        </v-row>

        <v-row class="mt-4">
          <v-col cols="12" md="6">
            <v-text-field
              v-model="search"
              label="Search (Feature not implemented)"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              dense
              disabled
            />
          </v-col>
          <v-col cols="12" md="6" class="text-right">
            <v-card flat class="pa-2 grey lighten-4 text-center">
              <strong>Recently Viewed... (Feature not implemented)</strong>
            </v-card>
          </v-col>
        </v-row>

        <v-row v-if="loadingRecipes" class="mt-8 justify-center">
             <v-progress-circular indeterminate color="primary"></v-progress-circular>
         </v-row>
         <v-row v-if="error" class="mt-8">
             <v-col>
                 <v-alert type="warning" dense>{{ error }}</v-alert>
             </v-col>
         </v-row>

        <v-row v-if="!loadingRecipes && !error && recipes.length > 0" class="mt-8">
          <v-col cols="12">
            <h3>Your Recipes......</h3>
          </v-col>

          <v-col cols="12" sm="6" md="4" lg="3" v-for="recipe in recipes" :key="recipe.id">
             <v-card @click="$router.push(`/recipe/details/${recipe.id}`)">
               <v-img :src="recipe.image_url || 'https://via.placeholder.com/300x150?text=No+Image'" height="150px" cover>
                 <template v-slot:placeholder>
                   <v-row class="fill-height ma-0" align="center" justify="center">
                     <v-progress-circular indeterminate color="grey lighten-5"></v-progress-circular>
                   </v-row>
                 </template>
               </v-img>
              <v-card-title>{{ recipe.name }}</v-card-title>
              <v-card-subtitle>
                 {{ recipe.cuisine?.name }} | {{ recipe.category?.name }}
               </v-card-subtitle>
            </v-card>
          </v-col>
        </v-row>
         <v-row v-if="!loadingRecipes && !error && recipes.length === 0" class="mt-8">
             <v-col>
                 <p class="text-center grey--text">No recipes found. Add one!</p>
             </v-col>
         </v-row>

        <v-row justify="end" class="mt-4">
           <v-btn color="black" dark @click="goToRecipes">
            Go to All Recipes
            <v-icon end>mdi-arrow-right</v-icon>
          </v-btn>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>
<script>
import { useAuthStore } from '../stores/auth'; // Import auth store

export default {
  name: 'HomeView', // Changed name for clarity
  data() {
    return {
      // User details will be fetched
      userData: { user_name: 'there' }, // Default greeting
      search: '',
      recipes: [], // Start with an empty array
      loadingUser: false,
      loadingRecipes: false,
      error: null
    }
  },
  computed: {
     // Computed property to display username safely
     userGreetingName() {
       return this.userData?.user_name || 'there';
     }
  },
  async mounted() {
    // Fetch both user data and recipes when component mounts
    await this.fetchUserProfile();
    await this.fetchRecentRecipes();
  },
  methods: {
    async fetchUserProfile() {
      const authStore = useAuthStore();
      const token = authStore.token;
      this.error = null;

      if (!token) return; // Don't fetch if not logged in

      this.loadingUser = true;
      try {
        const response = await fetch("http://127.0.0.1:8000/users/me", {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Failed to fetch user data');
        this.userData = await response.json();
      } catch (err) {
        console.error("Error fetching user for home:", err);
        // Don't necessarily log out here, just use default greeting
        this.error = "Could not load user details.";
      } finally {
        this.loadingUser = false;
      }
    },

    async fetchRecentRecipes() {
      const authStore = useAuthStore();
      const token = authStore.token;
      this.error = null; // Clear previous errors, maybe separate recipe error?

      if (!token) return; // Don't fetch if not logged in

      this.loadingRecipes = true;
      try {
        // Fetch recipes (maybe limit the results in backend later?)
        const response = await fetch("http://127.0.0.1:8000/recipe", {
           headers: { "Authorization": `Bearer ${token}` }
        });

        if (response.status === 401 || response.status === 403) {
           alert("Authentication failed. Please log in again.");
           authStore.logout();
           this.$router.push('/login');
           throw new Error('Unauthorized');
        }

        if (!response.ok) {
           throw new Error(`Failed to fetch recipes (${response.status})`);
        }
        const allRecipes = await response.json();
        // Show maybe the first 4 recipes on the home page
        this.recipes = allRecipes.slice(0, 4);

      } catch (err) {
         if (err.message !== 'Unauthorized') {
           console.error("Error fetching recipes for home:", err);
           this.error = "Could not load recipes.";
           this.recipes = []; // Clear recipes on error
         }
      } finally {
        this.loadingRecipes = false;
      }
    },
     goToRecipes() {
       this.$router.push('/recipes'); // Correct navigation
     },
    
  }
}
</script>