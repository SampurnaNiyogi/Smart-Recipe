<template>
  <v-app>
    <v-main>
      <v-container>
        <v-card class="pa-6 mt-8" outlined>
          <v-card-title>Add/Edit your recipes</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field label="Recipe Name" v-model="form.name" />
                <v-text-field label="Add Description" v-model="form.description" />

                <v-text-field label="Add Ingredient" v-model="form.ingredients" />
                <v-text-field label="Add Instruction" v-model="form.instructions" />
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  label="Upload Image URL"
                  v-model="form.image_url"
                />

                <v-select
                  :items="categories"
                  label="Choose category"
                  v-model="form.category_id"
                  item-title="name"
                  item-value="_id"
                />

                <v-select
                  :items="cuisines"
                  label="Choose cuisine"
                  v-model="form.cuisine_id"
                  item-title="name"
                  item-value="_id"
                />
                <v-select 
                  :items="diets"
                  label="Choose diets"
                  v-model="form.diet_id"
                  item-title="name"
                  item-value="_id"
                />
              </v-col>
            </v-row>

            <v-btn color="pink darken-1" class="mt-4" @click="submitRecipe">Submit</v-btn>
          </v-card-text>
        </v-card>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { useAuthStore } from '../stores/auth';
export default {
  data() {
    return {
      cuisines: [],
      categories: [],
      diets: [],
      form: {
        name: '',
        description: '',
        ingredients: '',
        instructions: '',
        category_id: '',
        cuisine_id: '',
        diet_id: '',
        image_url: '',
      },
      
    }
  },
  mounted() {
    this.fetchCuisines();
    this.fetchCategories();
    this.fetchDiets();
  },
  methods: {
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
    async submitRecipe() {
      // --- Import and use the auth store ---
      const authStore = useAuthStore(); // Make sure this line is inside the method or component setup
      const token = authStore.token;

      // --- Check if token exists ---
      if (!token) {
        alert("Authentication error: You are not logged in.");
        this.$router.push('/login'); // Redirect to login
        return;
      }
      // --- End of new code ---

      try {
        const response = await fetch("http://127.0.0.1:8000/create_recipe", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            // --- Add the Authorization header ---
            "Authorization": `Bearer ${token}`
            // --- End of new code ---
          },
          body: JSON.stringify(this.form)
        });

        // --- Handle potential 401/403 Unauthorized errors ---
        if (response.status === 401 || response.status === 403) {
           alert("Authentication failed. Please log in again.");
           authStore.logout(); // Clear token
           this.$router.push('/login');
           return;
        }
        // --- End of new code ---

        if (!response.ok) {
          const errorData = await response.json();
          // Display more specific backend error if available
          alert(`Error creating recipe: ${errorData.detail || response.statusText}`);
          return;
        }

        const result = await response.json();
        console.log("Recipe Created:", result);
        alert("Recipe Created Successfully");

        // Reset form after submission
        this.form = {
          name: '',
          description: '',
          ingredients: '',
          // Ensure 'instructions' is reset, not 'instruction'
          instructions: '', // <--- Fix typo if present
          category_id: '',
          cuisine_id: '',
          diet_id: '',
          image_url: ''
        };

      } catch (err) {
        console.error("Failed to create recipe:", err);
        // Provide more context for network or other errors
        alert(`Something went wrong while creating the recipe: ${err.message}`);
      }
    }
  }
}
  

    
    
</script>
