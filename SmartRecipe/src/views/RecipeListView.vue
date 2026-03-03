<template>
  <v-container>
    <v-row class="mt-8">
      <v-col cols="12" md="8">
        <div class="d-flex justify-space-between align-center mb-6">
          <h2 class="text-h4 text-teal-darken-3 font-weight-bold">Explore Recipes</h2>
          <v-btn color="teal" prepend-icon="mdi-plus" @click="$router.push('/add')" class="d-md-none">
            Add
          </v-btn>
        </div>

        <v-row v-if="loading">
          <v-col cols="12" sm="6" lg="4" v-for="n in 6" :key="n">
            <v-skeleton-loader type="card"></v-skeleton-loader>
          </v-col>
        </v-row>

        <v-row v-else-if="recipes.length === 0">
          <v-col cols="12">
            <v-card class="text-center pa-10 bg-grey-lighten-4" elevation="0" border>
              <v-icon size="64" color="grey">mdi-food-off</v-icon>
              <h3 class="text-h6 mt-4 text-grey-darken-1">No recipes found.</h3>
              <p class="text-body-2 text-grey">Try adjusting your filters or add a new recipe.</p>
            </v-card>
          </v-col>
        </v-row>

        <v-row v-else>
          <v-col cols="12" sm="6" lg="4" v-for="recipe in recipes" :key="recipe._id">
            <v-card hover @click="$router.push(`/recipe/details/${recipe._id}`)" class="h-100 d-flex flex-column rounded-lg">
              <v-img :src="recipe.image_url || 'https://placehold.co/400x300/E0F2F7/00695C?text=No+Image'" height="180px" cover></v-img>
              <v-card-title class="text-truncate pt-4">{{ recipe.name }}</v-card-title>
              <v-card-text class="flex-grow-1 pb-4">
                <div class="d-flex flex-wrap gap-2">
                  <v-chip size="small" color="teal" variant="flat" v-if="recipe.cuisine">
                    <v-icon start icon="mdi-earth"></v-icon>
                    {{ recipe.cuisine.name }}
                  </v-chip>
                  <v-chip size="small" color="indigo" variant="outlined" v-if="recipe.category">
                    {{ recipe.category.name }}
                  </v-chip>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-col>

      <v-col cols="12" md="4">
        <v-btn color="teal" block size="large" prepend-icon="mdi-plus" class="mb-6 d-none d-md-flex" elevation="2" @click="$router.push('/add')">
          Create New Recipe
        </v-btn>

        <v-card elevation="2" class="pa-4 rounded-lg" style="position: sticky; top: 88px;">
          <v-card-title class="text-h6 font-weight-bold d-flex align-center px-0">
            <v-icon start color="teal">mdi-filter-variant</v-icon>
            Filter Recipes
          </v-card-title>
          <v-card-text class="px-0 pt-4">
            <v-select
              :items="cuisines"
              item-title="name"
              item-value="_id"
              label="Cuisines"
              v-model="selectedCuisine"
              variant="outlined"
              density="comfortable"
              prepend-inner-icon="mdi-earth"
              clearable
              hide-details
              class="mb-4"
            ></v-select>
            <v-select
              :items="categories"
              item-title="name"
              item-value="_id"
              label="Categories"
              v-model="selectedCategory"
              variant="outlined"
              density="comfortable"
              prepend-inner-icon="mdi-shape"
              clearable
              hide-details
              class="mb-4"
            ></v-select>
            <v-select
              :items="diets"
              item-title="name"
              item-value="_id"
              label="Diets"
              v-model="selectedDiet"
              variant="outlined"
              density="comfortable"
              prepend-inner-icon="mdi-leaf"
              clearable
              hide-details
            ></v-select>

            <v-btn block color="teal-darken-2" size="large" class="mt-6" @click="applyFilters" prepend-icon="mdi-magnify">
              Apply Filters
            </v-btn>

            <v-btn block variant="text" color="grey-darken-1" class="mt-2" @click="clearFilters" prepend-icon="mdi-refresh">
              Reset
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { useAuthStore } from '../stores/auth'

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
      selectedDiet: null,
      loading: false
    }
  },
  mounted() {
    this.fetchRecipes()
    this.fetchCuisines()
    this.fetchCategories()
    this.fetchDiets()
  },
  methods: {
    fetchRecipes(params = {}) {
      const authStore = useAuthStore()
      const token = authStore.token

      if (!token) {
        alert("Your session may have expired. Please log in again.")
        authStore.logout()
        this.$router.push('/login')
        return
      }

      this.loading = true

      let url = "http://127.0.0.1:8000/recipe"
      const qs = new URLSearchParams(params).toString()
      if (qs) url += "?" + qs

      fetch(url, {
         headers: {
           "Authorization": `Bearer ${token}`
         }
      })
        .then(res => {
           if (res.status === 401 || res.status === 403) {
             alert("Authentication failed. Please log in again.")
             authStore.logout()
             this.$router.push('/login')
             throw new Error('Unauthorized')
           }
          if (!res.ok) {
             throw new Error(`Failed to fetch recipes (${res.status} ${res.statusText})`)
          }
          return res.json()
        })
        .then(data => {
          this.recipes = data
        })
        .catch(err => {
           if (err.message !== 'Unauthorized') {
             console.error(err)
             alert(`Could not load recipes: ${err.message}`)
             this.recipes = []
           }
        })
        .finally(() => {
          this.loading = false
        })
    },
    fetchCuisines() {
      fetch("http://127.0.0.1:8000/cuisines")
        .then(res => res.json())
        .then(data => {
          this.cuisines = data
        })
    },
    fetchCategories() {
      fetch("http://127.0.0.1:8000/categories")
        .then(res => res.json())
        .then(data => {
          this.categories = data
        })
    },
    fetchDiets() {
      fetch("http://127.0.0.1:8000/diets")
        .then(res => res.json())
        .then(data => {
          this.diets = data
        })
    },
    applyFilters() {
      const params = {}
      if (this.selectedCuisine) params.cuisine_id = this.selectedCuisine
      if (this.selectedCategory) params.category_id = this.selectedCategory
      if (this.selectedDiet) params.diet_id = this.selectedDiet
      this.fetchRecipes(params)
    },
    clearFilters() {
      this.selectedCuisine = null
      this.selectedCategory = null
      this.selectedDiet = null
      this.fetchRecipes()
    }
  }
}
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}
</style>