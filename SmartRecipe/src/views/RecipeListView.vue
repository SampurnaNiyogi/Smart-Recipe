<template>
  <v-container>
        <v-row class="mt-8">
          <!-- Recipe List -->
          <v-col cols="12" md="8">
            <h3>Recipes</h3>
            <v-row>
              <v-col cols="6" md="4" v-for="recipe in recipes" 
                      :key="recipe._id">
                <v-card @click = "$router.push(`/recipe/details/${recipe._id}`)">
                  <v-img :src="recipe.image_url" height="140px" />
                  <v-card-text>
                    <strong>{{ recipe.name }}</strong><br />
                      • Cuisine: {{ recipe.cuisine ? recipe.cuisine.name : 'N/A' }}<br />
                      • Category: {{ recipe.category ? recipe.category.name : 'N/A' }}
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-col>

          <!-- Filters & Add Button -->
          <v-col cols="12" md="4">
            <v-btn block outlined class="mb-4" @click="$router.push('/add')">
              + Add new recipe
            </v-btn>

            <v-card outlined>
              <v-card-title class="text-subtitle-1">Filter Recipe By….</v-card-title>
              <v-card-text>
                <v-select 
                  :items="cuisines"
                  item-title="name"
                  item-value="_id"
                  label="Cuisines"
                  v-model="selectedCuisine"
                />
                <v-select 
                  :items="categories"
                  item-title="name"
                  item-value="_id"
                  label="Categories"
                  v-model="selectedCategory"
                />
                <v-select 
                  :items="diets"
                  item-title="name"
                  item-value="_id"
                  label="Diets"
                  v-model="selectedDiet"
                />
                <!-- The Filter Button -->
                <v-btn block color="primary" class="mt-3" @click="applyFilters">
                  Filter Recipes
                </v-btn>

                <!-- Optional: Clear all filters -->
                <v-btn block outlined color="grey" class="mt-2" @click="clearFilters">
                  Clear Filters
                </v-btn>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    
</template>

<script>
import { useAuthStore } from '../stores/auth';
export default {
  name: "RecipeListView",
  data() {
    return {
      recipes: [],
      cuisines: [],
      categories: [],
      diets: [],
      selectedCuisine: null,
      selectedCategory: null,
      selectedDiet: null
    }
  },
  mounted() {
    this.fetchRecipes();
    this.fetchCuisines();
    this.fetchCategories();
    this.fetchDiets();
  },
  methods: {
    fetchRecipes(params = {}) {
      const authStore = useAuthStore(); // Make sure this line is inside the method or component setup
      const token = authStore.token;

      // --- Check if token exists ---
       if (!token) {
         console.error("Authentication error: No token found.");
         // Optionally redirect to login or show a message
         // This might happen if the user's session expires and they try to filter
         // For the initial load, the router guard should prevent access anyway.
         alert("Your session may have expired. Please log in again.");
         authStore.logout(); // Clear any invalid state
         this.$router.push('/login');
         return;
       }
       // --- End of new code ---


      let url = "http://127.0.0.1:8000/recipe";
      const qs = new URLSearchParams(params).toString();
      if (qs) url += "?" + qs;

      fetch(url, {
         // --- Add headers object with Authorization ---
         headers: {
           "Authorization": `Bearer ${token}`
         }
         // --- End of new code ---
      })
        .then(res => {
          // --- Handle potential 401/403 Unauthorized errors ---
           if (res.status === 401 || res.status === 403) {
             alert("Authentication failed. Please log in again.");
             authStore.logout(); // Use the store's logout action
             this.$router.push('/login');
             throw new Error('Unauthorized'); // Stop further processing
           }
          // --- End of new code ---
          if (!res.ok) {
             // Throw an error to be caught by the .catch block
             throw new Error(`Failed to fetch recipes (${res.status} ${res.statusText})`);
          }
          return res.json();
        })
        .then(data => {
          this.recipes = data;
        })
        .catch(err => {
           // Avoid processing if it was an Unauthorized error we already handled
           if (err.message !== 'Unauthorized') {
             console.error("Error fetching recipes:", err);
             // Show user-friendly error message, e.g., using a snackbar or alert
             alert(`Could not load recipes: ${err.message}`);
             this.recipes = []; // Clear recipes on error
           }
        });
    },
    fetchCuisines() {
      fetch("http://127.0.0.1:8000/cuisines")
        .then(res => res.json())
        .then(data => {
          this.cuisines = data;
        });
    },
    fetchCategories() {
      fetch("http://127.0.0.1:8000/categories")
        .then(res => res.json())
        .then(data => {
          this.categories = data;
        });
    },
    fetchDiets() {
      fetch("http://127.0.0.1:8000/diets")
        .then(res => res.json())
        .then(data => {
          this.diets = data;
        });
    },
    applyFilters() {
      const params = {};
      if (this.selectedCuisine) params.cuisine_id = this.selectedCuisine;
      if (this.selectedCategory) params.category_id = this.selectedCategory;
      if (this.selectedDiet) params.diet_id = this.selectedDiet;
      this.fetchRecipes(params);
    },
    clearFilters() {
      this.selectedCuisine = null;
      this.selectedCategory = null;
      this.fetchRecipes();
    }
  }

};
</script>
