<template>
  <v-container>
        <v-row class="mt-8">
          <!-- Main Recipe Column -->
          <v-col cols="12">
            <v-btn variant="text" @click="$router.back()" class="mb-4">← Back to Recipes</v-btn>
            <v-card :loading="loading">
              <v-img :src="recipe.image_url || 'https://placehold.co/1200x400/E0F2F7/00695C?text=No+Image'" height="300px" cover />
              <v-card-title class="text-h5 mt-2">{{ recipe.name }}</v-card-title>
              <v-card-subtitle>
                {{ recipe.cuisine?.name }} | {{ recipe.category?.name }} | {{ recipe.diet?.name }}
              </v-card-subtitle>
              <v-card-text>
                <p class="mb-4">{{ recipe.description || 'No description available.' }}</p>
                <v-divider class="my-4"></v-divider>
                <strong>Ingredients:</strong>
                <p>{{ recipe.ingredients }}</p>
                <v-divider class="my-4"></v-divider>
                <strong>Instructions:</strong>
                <p style="white-space: pre-wrap;">{{ recipe.instructions }}</p>
              </v-card-text>
            </v-card>
             <v-alert v-if="error" type="error" dense class="mt-4">{{ error }}</v-alert>
          </v-col>
        </v-row>

        <!-- NEW: Similar Recipes Section -->
        <v-row class="mt-8" v-if="similarRecipes.length > 0">
          <v-col cols="12">
            <h3 class="text-h6">You Might Also Like</h3>
            <v-divider class="my-4"></v-divider>
          </v-col>
          <v-col v-for="similar in similarRecipes" :key="similar._id" cols="12" sm="6" md="3">
            <v-card :to="`/recipe/details/${similar._id}`">
              <v-img :src="similar.image_url || 'https://placehold.co/400x300/E0F2F7/00695C?text=No+Image'" height="150px" cover />
              <v-card-title class="text-subtitle-1">{{ similar.name }}</v-card-title>
              <v-card-subtitle>{{ similar.cuisine?.name }}</v-card-subtitle>
            </v-card>
          </v-col>
        </v-row>
        <!-- End of new section -->

      </v-container>
    
</template>

<script>
import { useAuthStore } from '../stores/auth';
export default {
  name: "RecipeDetailView",
  data() {
    return {
      recipe: {},
      similarRecipes: [], // New data property for recommendations
      loading: false,
      error: ""
    };
  },
  mounted() {
    this.fetchDataForRecipe();
  },
  watch: {
    // When the route changes (e.g., clicking a similar recipe), refetch everything
    "$route.params.id"() {
      // Reset state before fetching new data
      this.recipe = {};
      this.similarRecipes = [];
      this.fetchDataForRecipe();
    }
  },
  methods: {
    async fetchDataForRecipe() {
      // This function will now orchestrate both API calls
      const id = this.$route.params.id;
      if (!id) return;
      
      await this.fetchRecipe(id);
      // Only fetch similar recipes if the main recipe was fetched successfully
      if (this.recipe && this.recipe._id) {
        await this.fetchSimilarRecipes(id);
      }
    },
    async fetchRecipe(id) {
      const authStore = useAuthStore();
      const token = authStore.token;
      if (!token) {
        this.error = "Authentication error."; this.$router.push('/login'); return;
      }

      this.loading = true;
      this.error = "";
      try {
        const res = await fetch(`http://127.0.0.1:8000/recipe/${id}`, {
           headers: { "Authorization": `Bearer ${token}` }
        });
        if (res.status === 401) { authStore.logout(); this.$router.push('/login'); throw new Error('Unauthorized'); }
        if (!res.ok) throw new Error(`Fetch failed (${res.status})`);
        this.recipe = await res.json();
      } catch (e) {
        if (e.message !== 'Unauthorized') this.error = e.message || "Error fetching recipe details.";
      } finally {
        this.loading = false;
      }
    },
    // NEW METHOD: Fetch Similar Recipes
    async fetchSimilarRecipes(id) {
      const authStore = useAuthStore();
      const token = authStore.token;
      if (!token) return; // Should already be handled, but good practice

      try {
        const res = await fetch(`http://127.0.0.1:8000/recommendations/similar/${id}`, {
           headers: { "Authorization": `Bearer ${token}` }
        });
        if (res.status === 401) { return; } // Don't bother the user again
        if (!res.ok) throw new Error(`Failed to fetch similar recipes (${res.status})`);
        this.similarRecipes = await res.json();
      } catch (e) {
        console.error("Could not load similar recipes:", e.message);
        // Don't show a blocking error for this, it's non-critical
      }
    }
  }
};
</script>

