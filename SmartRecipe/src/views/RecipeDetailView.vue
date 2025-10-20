<template>
  <v-container>
    <v-row class="mt-8">
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
          <p class="text-caption text-grey">Click an ingredient to find substitutes</p>
          <div class="mt-2">
            <v-chip
              v-for="(ingredient, i) in ingredientList"
              :key="i"
              class="ma-1"
              @click="findSubstitutes(ingredient)"
              color="teal"
              variant="outlined"
            >
              <v-icon start icon="mdi-help-circle-outline"></v-icon>
              {{ ingredient }}
            </v-chip>
          </div>
          <v-divider class="my-4"></v-divider>
          <strong>Instructions:</strong>
          <p style="white-space: pre-wrap;">{{ recipe.instructions }}</p>
        </v-card-text>
        </v-card>
        
      </v-col>
    </v-row>

    <v-dialog v-model="substituteDialog" max-width="400">
      <v-card>
        <v-card-title>
          Substitutes for "{{ selectedIngredient }}"
        </v-card-title>
        <v-card-text>
          <v-list v-if="substitutes.length > 0">
            <v-list-item
              v-for="(sub, i) in substitutes"
              :key="i"
              :title="sub"
            ></v-list-item>
          </v-list>
          <p v-else>No common substitutes found in our database.</p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="substituteDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
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
      error: "",
      substituteDialog: false, 
      selectedIngredient: '', 
      substitutes: []
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
  computed: {
    ingredientList() {
      if (!this.recipe.ingredients) return [];
      // Split by comma and trim whitespace
      return this.recipe.ingredients.split(',').map(item => item.trim());
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
    },
    async findSubstitutes(ingredient) {
      // Clean up the ingredient string to find the main noun
      // e.g., "1/4 cup Onions" -> "Onions"
      // e.g., "tofu (firm)" -> "tofu"
      const cleanIngredient = ingredient
        .replace(/[\d/]+( cup| tbsp| tsp| tablespoon| teaspoon)?s?/i, '')
        .replace(/\(.*\)/, '') // Remove text in parentheses
        .trim();
        
      if (!cleanIngredient) return;

      this.selectedIngredient = ingredient; // Show the full original name in dialog
      this.substitutes = [];
      this.substituteDialog = true;
      
      const authStore = useAuthStore();
      const token = authStore.token;
      if (!token) return;

      try {
        const res = await fetch(`http://127.0.0.1:8000/recipe/substitutes/${cleanIngredient}`, {
           headers: { "Authorization": `Bearer ${token}` }
        });
        if (!res.ok) throw new Error("Could not fetch substitutes");
        this.substitutes = await res.json();
      } catch (e) {
        console.error("Substitute Error:", e.message);
        this.substitutes = []; // Reset on error
      }
    }
  }
};
</script>

