<template>
  <v-app>
    <v-main>
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
                    • {{ recipe.cuisine_id }}<br />
                    • {{ recipe.category_id}}
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
    </v-main>
  </v-app>
</template>

<script>
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
      let url = "http://127.0.0.1:8000/recipe";
      const qs = new URLSearchParams(params).toString();
      if (qs) url += "?" + qs;

      fetch(url)
        .then(res => res.json())
        .then(data => {
          this.recipes = data;
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
