<template>
  <v-container>

    <v-row class="mt-10">
      <v-col cols="12">
        <h2 class="text-h4">Welcome back, {{ userGreetingName }}!</h2>
        <h3 class="text-subtitle-1">What would you like to cook today?</h3>
      </v-col>
    </v-row>

    <v-row v-if="error" class="mt-8">
      <v-col cols="12">
        <v-alert type="error" outlined>{{ error }}</v-alert>
      </v-col>
    </v-row>

    <v-row class="mt-4">
      <v-col cols="12">
        <v-text-field
          v-model="searchQuery"
          label="Search by name or ingredients (e.g., 'chicken garlic')"
          placeholder="What do you have in your pantry?"
          prepend-inner-icon="mdi-magnify"
          variant="solo"
          clearable
          @keydown.enter="performSearch"
          @click:clear="clearSearch" >
          <template v-slot:append-inner>
            <v-btn @click="performSearch" color="teal" icon="mdi-arrow-right" variant="flat" :loading="loadingSearch"></v-btn>
          </template>
        </v-text-field>
      </v-col>
    </v-row>
    <div v-if="showingSearchResults">
      <v-row class="mt-8">
        <v-col cols="12" class="d-flex justify-space-between align-center">
          <h3 class="text-h5">Search Results for "{{ displayedSearchQuery }}"</h3>
          <v-btn variant="text" @click="clearSearch">Clear Search</v-btn>
        </v-col>
        <v-col v-if="loadingSearch" cols="12">
           <v-progress-linear indeterminate color="teal"></v-progress-linear>
        </v-col>
        <v-col v-else-if="searchResults.length === 0" cols="12">
          <v-alert type="info" outlined>No recipes found matching your search.</v-alert>
        </v-col>
         <v-col v-else v-for="recipe in searchResults" :key="recipe._id" cols="12" sm="6" md="4" lg="3">
           <v-card :to="`/recipe/details/${recipe._id}`">
             <v-img :src="recipe.image_url || 'https://placehold.co/400x300/E0F2F7/00695C?text=No+Image'" height="150px" cover />
             <v-card-title>{{ recipe.name }}</v-card-title>
             <v-card-subtitle>{{ recipe.cuisine?.name }}</v-card-subtitle>
           </v-card>
         </v-col>
      </v-row>
    </div>
    <div v-else>
      <v-row v-if="error" class="mt-8">
        <v-col cols="12">
          <v-alert type="error" outlined>{{ error }}</v-alert>
        </v-col>
      </v-row>

      <v-row class="mt-8" v-if="!loadingSeasonal && seasonalRecipes.length > 0">
         <v-col cols="12">
            <h3 class="text-h5">Seasonal Suggestions</h3>
            <v-divider class="my-4"></v-divider>
          </v-col>
          <v-col v-for="recipe in seasonalRecipes" :key="recipe._id" cols="12" sm="6" md="4" lg="3">
            <v-card @click = "$router.push(`/recipe/details/${recipe._id}`)">
              <v-img :src="recipe.image_url || 'https://placehold.co/400x300/E0F2F7/00695C?text=No+Image'" height="150px" cover />
              <v-card-title>{{ recipe.name }}</v-card-title>
              <v-card-subtitle>{{ recipe.cuisine?.name }}</v-card-subtitle>
            </v-card>
          </v-col>
      </v-row>

      <v-row class="mt-8" v-if="!loadingHistory && historyRecipes.length > 0">
         <v-col cols="12">
            <h3 class="text-h5">Based on Your History</h3>
            <v-divider class="my-4"></v-divider>
          </v-col>
          <v-col v-for="recipe in historyRecipes" :key="recipe._id" cols="12" sm="6" md="4" lg="3">
            <v-card :to="`/recipe/details/${recipe._id}`">
              <v-img :src="recipe.image_url || 'https://placehold.co/400x300/E0F2F7/00695C?text=No+Image'" height="150px" cover />
              <v-card-title>{{ recipe.name }}</v-card-title>
              <v-card-subtitle>{{ recipe.cuisine?.name }}</v-card-subtitle>
            </v-card>
          </v-col>
      </v-row>

      <v-row class="mt-8" v-if="!loadingPreferred && preferredRecipes.length > 0">
         <v-col cols="12">
            <h3 class="text-h5">From Your Favorite Cuisine</h3>
            <v-divider class="my-4"></v-divider>
          </v-col>
          <v-col v-for="recipe in preferredRecipes" :key="recipe._id" cols="12" sm="6" md="4" lg="3">
            <v-card :to="`/recipe/details/${recipe._id}`">
              <v-img :src="recipe.image_url || 'https://placehold.co/400x300/E0F2F7/00695C?text=No+Image'" height="150px" cover />
              <v-card-title>{{ recipe.name }}</v-card-title>
              <v-card-subtitle>{{ recipe.cuisine?.name }}</v-card-subtitle>
            </v-card>
          </v-col>
      </v-row>

      <v-row class="mt-8" v-if="!loadingRecipes && recipes.length > 0">
         <v-col cols="12">
            <h3 class="text-h5">Recently Added</h3>
            <v-divider class="my-4"></v-divider>
          </v-col>
          <v-col v-for="recipe in recipes" :key="recipe._id" cols="12" sm="6" md="4" lg="3">
             <v-card :to="`/recipe/details/${recipe._id}`">
                <v-img :src="recipe.image_url || 'https://placehold.co/400x300/E0F2F7/00695C?text=No+Image'" height="150px" cover />
                <v-card-title>{{ recipe.name }}</v-card-title>
                <v-card-subtitle>{{ recipe.cuisine?.name }}</v-card-subtitle>
             </v-card>
          </v-col>
      </v-row>


      <v-row v-if="loadingRecipes || loadingSeasonal || loadingHistory || loadingPreferred" class="mt-8">
         <v-col v-for="n in 4" :key="n" cols="12" sm="6" md="4" lg="3">
            <v-skeleton-loader type="card"></v-skeleton-loader>
          </v-col>
      </v-row>

      <v-row class="mt-12">
         <v-col class="text-center">
            <v-btn color="teal" @click="goToRecipes">View All Recipes</v-btn>
          </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script>
// ... (Your <script> section is perfect, no changes needed)
import { useAuthStore } from '../stores/auth';

export default {
  name: 'HomeView',
  data() {
    return {
      userData: { user_name: 'there' },
      recipes: [],
      seasonalRecipes: [],
      historyRecipes: [],
      preferredRecipes: [],
      loadingUser: false,
      loadingRecipes: false,
      loadingSeasonal: false,
      loadingHistory: false,
      loadingPreferred: false,
      searchQuery: '',
      error: null,
      displayedSearchQuery: '', // To keep query visible while searching
      searchResults: [],
      loadingSearch: false,
      showingSearchResults: false // Flag to toggle view
    }
  },
  computed: {
     userGreetingName() {
       return this.userData?.user_name || 'there';
     }
  },
  async mounted() {
    // Fetch all data in parallel for a faster load time
    Promise.all([
      this.fetchUserProfile(),
      this.fetchRecentRecipes(),
      this.fetchSeasonalRecipes(),
      this.fetchHistoryRecipes(),
      this.fetchPreferredRecipes()
    ]);
  },
  methods: {
    async fetchPreferredRecipes() {
      const authStore = useAuthStore();
      const token = authStore.token;
      if (!token) return;
      this.loadingPreferred = true;
      try {
        const response = await fetch("http://127.0.0.1:8000/recommendations/preferred_cuisine", { headers: { "Authorization": `Bearer ${token}` } });
        if (response.status === 401) { return; }
        if (!response.ok) throw new Error(`Failed to fetch preferred recipes (${response.status})`);
        this.preferredRecipes = await response.json();
      } catch (err) {
        console.error("Error fetching preferred recipes:", err.message);
      } finally {
        this.loadingPreferred = false;
      }
    },
    async fetchHistoryRecipes() {
      const authStore = useAuthStore();
      const token = authStore.token;
      if (!token) return;
      this.loadingHistory = true;
      try {
        const response = await fetch("http://127.0.0.1:8000/recommendations/history", { headers: { "Authorization": `Bearer ${token}` } });
        if (response.status === 401) { return; }
        if (!response.ok) throw new Error(`Failed to fetch history recipes (${response.status})`);
        this.historyRecipes = await response.json();
      } catch (err) {
        console.error("Error fetching history recipes:", err.message);
      } finally {
        this.loadingHistory = false;
      }
    },
    async fetchUserProfile() {
      const authStore = useAuthStore();
      const token = authStore.token;
      if (!token) return;
      this.loadingUser = true;
      try {
        const response = await fetch("http://127.0.0.1:8000/users/me", { headers: { "Authorization": `Bearer ${token}` } });
        if (!response.ok) throw new Error('Failed to fetch user data');
        this.userData = await response.json();
      } catch (err) {
        console.error("Error fetching user for home:", err);
      } finally {
        this.loadingUser = false;
      }
    },
    async fetchRecentRecipes() {
      const authStore = useAuthStore();
      const token = authStore.token;
      if (!token) return;
      this.loadingRecipes = true;
      try {
        const response = await fetch("http://127.0.0.1:8000/recipe", { headers: { "Authorization": `Bearer ${token}` } });
        if (response.status === 401) { authStore.logout(); this.$router.push('/login'); return; }
        if (!response.ok) throw new Error(`Failed to fetch recipes (${response.status})`);
        const allRecipes = await response.json();
        this.recipes = allRecipes.slice(0, 4);
      } catch (err) {
        console.error("Error fetching recipes for home:", err.message);
        this.error = "Could not load your recipes.";
      } finally {
        this.loadingRecipes = false;
      }
    },
    async fetchSeasonalRecipes() {
      const authStore = useAuthStore();
      const token = authStore.token;
      if (!token) return;
      this.loadingSeasonal = true;
      try {
        const response = await fetch("http://127.0.0.1:8000/recommendations/seasonal", { headers: { "Authorization": `Bearer ${token}` } });
        if (response.status === 401) { return; }
        if (!response.ok) throw new Error(`Failed to fetch seasonal recipes (${response.status})`);
        this.seasonalRecipes = await response.json();
      } catch (err) {
        console.error("Error fetching seasonal recipes:", err.message);
        // Do not set the main error for this non-critical feature
      } finally {
        this.loadingSeasonal = false;
      }
    },
    goToRecipes() {
      this.$router.push('/recipes');
    },
    performSearch() {
      if (this.searchQuery.trim()) {
        this.$router.push({ path: '/recipes', query: { q: this.searchQuery } });
        this.searchQuery = ''; // Clear search bar after search
      }
    },
    async performSearch() {
      const query = this.searchQuery.trim();
      if (!query) {
        this.clearSearch(); // If search is empty, clear results
        return;
      }

      this.loadingSearch = true;
      this.showingSearchResults = true;
      this.displayedSearchQuery = query; // Store query for display
      this.searchResults = [];
      this.error = null; // Clear previous main errors

      const authStore = useAuthStore();
      const token = authStore.token;
      if (!token) {
        this.error = "Authentication error.";
        this.loadingSearch = false;
        return;
      }

      try {
        const params = new URLSearchParams({ search_query: query });
        const response = await fetch(`http://127.0.0.1:8000/recipe?${params.toString()}`, {
          headers: { "Authorization": `Bearer ${token}` }
        });

        if (response.status === 401) {
          authStore.logout();
          this.$router.push('/login');
          throw new Error('Unauthorized');
        }
        if (!response.ok) {
          throw new Error(`Search failed (${response.status})`);
        }
        this.searchResults = await response.json();

      } catch (err) {
        console.error("Error performing search:", err.message);
        this.error = `Could not perform search: ${err.message}`; // Show error
        this.searchResults = []; // Ensure results are empty on error
      } finally {
        this.loadingSearch = false;
      }
    },

    // --- NEW clearSearch METHOD ---
    clearSearch() {
      this.searchQuery = '';
      this.displayedSearchQuery = '';
      this.searchResults = [];
      this.showingSearchResults = false;
      this.loadingSearch = false;
      this.error = null; // Clear search-related errors
      // Note: We don't need to re-fetch recommendations here unless desired.
      // They will still be loaded from the initial `mounted()` call.
    }
  }
}
</script>