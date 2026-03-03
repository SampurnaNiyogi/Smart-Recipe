<template>
  <v-container fluid class="pa-0">
    <div class="bg-teal-darken-3 py-16 px-6 text-center text-white">
      <h1 class="text-h3 font-weight-bold mb-4">Welcome back, {{ userGreetingName }}!</h1>
      <h2 class="text-h5 font-weight-regular mb-8 text-teal-lighten-4">What are you craving today?</h2>
      
      <v-row justify="center">
        <v-col cols="12" sm="10" md="8" lg="6">
          <v-text-field
            v-model="searchQuery"
            placeholder="Search by name, ingredients, or dish type..."
            variant="solo"
            bg-color="white"
            color="teal-darken-3"
            clearable
            hide-details
            rounded="pill"
            elevation="6"
            class="search-input"
            @keydown.enter="performSearch"
            @click:clear="clearSearch"
          >
            <template v-slot:prepend-inner>
              <v-icon color="grey-darken-1" class="ml-2">mdi-magnify</v-icon>
            </template>
            <template v-slot:append-inner>
              <v-btn 
                color="teal" 
                icon="mdi-arrow-right" 
                variant="flat" 
                size="small"
                class="mr-1"
                :loading="loadingSearch"
                @click="performSearch"
              ></v-btn>
            </template>
          </v-text-field>
        </v-col>
      </v-row>
    </div>

    <v-container class="mt-8 mb-12">
      <v-alert v-if="error" type="error" variant="tonal" class="mb-8">{{ error }}</v-alert>

      <div v-if="showingSearchResults" class="mb-12">
        <div class="d-flex justify-space-between align-center mb-6">
          <h3 class="text-h5 font-weight-bold text-grey-darken-3">
            Search Results for "<span class="text-teal">{{ displayedSearchQuery }}</span>"
          </h3>
          <v-btn variant="text" color="grey-darken-1" @click="clearSearch" prepend-icon="mdi-close">Clear</v-btn>
        </div>
        
        <v-row v-if="loadingSearch">
          <v-col v-for="n in 4" :key="n" cols="12" sm="6" md="4" lg="3">
             <v-skeleton-loader type="card"></v-skeleton-loader>
          </v-col>
        </v-row>
        
        <v-row v-else-if="searchResults.length === 0">
          <v-col cols="12">
            <v-card class="pa-8 text-center bg-grey-lighten-4" elevation="0" border>
              <v-icon size="48" color="grey">mdi-magnify-remove-outline</v-icon>
              <p class="text-h6 mt-4 text-grey-darken-1">No recipes found matching your search.</p>
            </v-card>
          </v-col>
        </v-row>
        
        <v-row v-else>
           <v-col v-for="recipe in searchResults" :key="recipe._id" cols="12" sm="6" md="4" lg="3">
             <v-card hover class="h-100 rounded-lg" :to="`/recipe/details/${recipe._id}`">
               <v-img :src="recipe.image_url || 'https://placehold.co/400x300/E0F2F7/00695C?text=No+Image'" height="180px" cover />
               <v-card-title class="pt-3">{{ recipe.name }}</v-card-title>
               <v-card-subtitle class="pb-3 text-teal font-weight-medium">{{ recipe.cuisine?.name || 'Various' }}</v-card-subtitle>
             </v-card>
           </v-col>
        </v-row>
      </div>

      <div v-if="!showingSearchResults && seasonalRecipes.length > 0">
        <div class="d-flex align-center mb-6">
          <v-icon color="orange-darken-2" size="x-large" class="mr-3">mdi-white-balance-sunny</v-icon>
          <h3 class="text-h5 font-weight-bold text-grey-darken-3">Seasonal Suggestions</h3>
        </div>
        
        <v-row v-if="loadingSeasonal">
           <v-col v-for="n in 4" :key="n" cols="12" sm="6" md="4" lg="3">
              <v-skeleton-loader type="card"></v-skeleton-loader>
            </v-col>
        </v-row>

        <v-row v-else>
          <v-col v-for="recipe in seasonalRecipes" :key="recipe._id" cols="12" sm="6" md="4" lg="3">
            <v-card hover class="h-100 rounded-lg border-sm border-teal-lighten-4" @click="$router.push(`/recipe/details/${recipe._id}`)">
              <v-img :src="recipe.image_url || 'https://placehold.co/400x300/E0F2F7/00695C?text=No+Image'" height="180px" cover />
              <v-card-title class="pt-3">{{ recipe.name }}</v-card-title>
              <v-card-subtitle class="pb-3 text-teal font-weight-medium">{{ recipe.cuisine?.name || 'Various' }}</v-card-subtitle>
            </v-card>
          </v-col>
        </v-row>
      </div>

      <v-row class="mt-12">
         <v-col class="text-center">
            <v-btn color="teal-darken-2" size="x-large" elevation="4" @click="goToRecipes" prepend-icon="mdi-book-open-page-variant">
              Browse Full Recipe Directory
            </v-btn>
          </v-col>
      </v-row>
    </v-container>
  </v-container>
</template>

<script>
import { useAuthStore } from '../stores/auth';

export default {
  name: 'HomeView',
  data() {
    return {
      userData: { user_name: 'there' },
      recipes: [],
      seasonalRecipes: [],
      loadingUser: false,
      loadingRecipes: false,
      loadingSeasonal: false,
      searchQuery: '',
      error: null,
      displayedSearchQuery: '', 
      searchResults: [],
      loadingSearch: false,
      showingSearchResults: false 
    }
  },
  computed: {
     userGreetingName() {
       return this.userData?.user_name || 'there';
     }
  },
  async mounted() {
    Promise.all([
      this.fetchUserProfile(),
      this.fetchSeasonalRecipes(),
    ]);
  },
  methods: {
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
        console.error(err);
      } finally {
        this.loadingUser = false;
      }
    },
    async fetchSeasonalRecipes() {
      const authStore = useAuthStore();
      const token = authStore.token;
      if (!token) return;
      this.loadingSeasonal = true;
      try {
        const response = await fetch("http://127.0.0.1:8000/recommendations/seasonal", { headers: { "Authorization": `Bearer ${token}` } });
        if (response.status === 401) return;
        if (!response.ok) throw new Error('Failed to fetch seasonal recipes');
        this.seasonalRecipes = await response.json();
      } catch (err) {
        console.error(err.message);
      } finally {
        this.loadingSeasonal = false;
      }
    },
    goToRecipes() {
      this.$router.push('/recipes');
    },
    async performSearch() {
      const query = this.searchQuery?.trim();
      if (!query) {
        this.clearSearch(); 
        return;
      }

      this.loadingSearch = true;
      this.showingSearchResults = true;
      this.displayedSearchQuery = query; 
      this.searchResults = [];
      this.error = null; 

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
          return;
        }
        if (!response.ok) throw new Error("Search failed");
        
        this.searchResults = await response.json();
      } catch (err) {
        this.error = `Could not perform search: ${err.message}`; 
      } finally {
        this.loadingSearch = false;
      }
    },
    clearSearch() {
      this.searchQuery = '';
      this.displayedSearchQuery = '';
      this.searchResults = [];
      this.showingSearchResults = false;
      this.loadingSearch = false;
      this.error = null; 
    }
  }
}
</script>

<style scoped>
.search-input:deep(.v-field) {
  border-radius: 40px !important;
  padding-right: 8px;
}
</style>