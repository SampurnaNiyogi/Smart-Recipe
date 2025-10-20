<template>
  <v-app>
    <v-main>
      <v-container>
        <v-row class="mt-8">
          <!-- Recipe List -->
          <v-col cols="24" md="15">            
            <v-card>
              <v-img :src="recipe.image_url" height="140px"  />
              <v-card-text>
                <strong>{{ recipe.name }}</strong><br />
                Description: {{ recipe.description || 'No description available.' }}<br />
                 Cuisine : {{ recipe.cuisine ? recipe.cuisine.name : 'N/A' }}<br />
                Category: {{ recipe.category ? recipe.category.name : 'N/A' }}<br />
                Diet: {{ recipe.diet ? recipe.diet.name : 'N/A' }}<br />
                Ingredients: {{ recipe.ingredients }}<br />
                Instructions: {{ recipe.instructions }}
              </v-card-text>
            </v-card>
            <v-btn variant="text" @click="$router.back()">← Back</v-btn>
          </v-col>        

          </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { useAuthStore } from '../stores/auth';
export default {
  name: "RecipeDetailView",
  data() {
    return {
      recipe: {},
      loading: false,
      error: ""
    };
  },
  mounted() {
    this.fetchRecipe();
  },
  watch: {
    "$route.params.id"() { this.fetchRecipe(); }
  },
  methods: {
    async fetchRecipe() {
      const authStore = useAuthStore(); // Make sure this line is inside the method or component setup
      const token = authStore.token;
      // --- End of new code ---

      const id = this.$route.params.id;
      if (!id) { this.error = "Missing recipe id in route."; return; }

      // --- Check if token exists ---
      if (!token) {
        this.error = "Authentication error: You are not logged in.";
        alert(this.error);
        this.$router.push('/login'); // Redirect to login
        return;
      }
      // --- End of new code ---


      this.loading = true;
      this.error = "";
      try {
        const res = await fetch(`http://127.0.0.1:8000/recipe/${id}`, {
           // --- Add headers object with Authorization ---
           headers: {
             "Authorization": `Bearer ${token}`
           }
           // --- End of new code ---
        });

        // --- Handle potential 401/403 Unauthorized errors ---
        if (res.status === 401 || res.status === 403) {
           alert("Authentication failed. Please log in again.");
           authStore.logout(); // Clear token
           this.$router.push('/login');
           throw new Error('Unauthorized'); // Stop further processing
        }
        // --- End of new code ---


        if (!res.ok) {
           const errorText = await res.text(); // Get potential error details
           throw new Error(`Fetch failed (${res.status} ${res.statusText}): ${errorText}`);
        }
        this.recipe = await res.json();

      } catch (e) {
         if (e.message !== 'Unauthorized') { // Avoid duplicate alerts
           this.error = e.message || "Error fetching recipe details.";
           console.error("Error fetching recipe:", e);
           alert(this.error); // Notify user
           this.recipe = {}; // Clear potentially stale data
         }
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
