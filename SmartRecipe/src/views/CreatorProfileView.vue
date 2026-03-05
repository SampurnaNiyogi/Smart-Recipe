<template>
  <v-container>
    <v-row class="mt-8">
      <v-col cols="12">
        <v-btn variant="text" @click="$router.back()" class="mb-6" prepend-icon="mdi-arrow-left">
          Back
        </v-btn>
        
        <div class="d-flex align-center mb-8">
          <v-avatar color="teal-darken-2" size="72" class="mr-4 elevation-3">
            <span class="text-h3 text-white" v-if="creatorName">{{ creatorName.charAt(0).toUpperCase() }}</span>
          </v-avatar>
          <div>
            <h2 class="text-h4 font-weight-bold text-teal-darken-4">{{ creatorName }}'s Recipes</h2>
            <p class="text-grey-darken-1 text-subtitle-1">Check out all the recipes shared by this creator!</p>
          </div>
        </div>

        <v-alert v-if="error" type="error" variant="tonal" class="mb-4">{{ error }}</v-alert>

        <v-row v-if="loading">
          <v-col v-for="n in 4" :key="n" cols="12" sm="6" md="4" lg="3">
            <v-skeleton-loader type="card"></v-skeleton-loader>
          </v-col>
        </v-row>

        <v-row v-else-if="recipes.length === 0">
          <v-col cols="12">
            <v-card class="text-center pa-10 bg-grey-lighten-4" elevation="0" border>
              <v-icon size="64" color="grey lighten-1">mdi-silverware-fork-knife</v-icon>
              <h3 class="text-h6 mt-4 text-grey-darken-1">This user hasn't posted any recipes yet.</h3>
            </v-card>
          </v-col>
        </v-row>

        <v-row v-else>
          <v-col cols="12" sm="6" md="4" lg="3" v-for="recipe in recipes" :key="recipe._id">
            <v-card @click="$router.push(`/recipe/details/${recipe._id}`)" hover class="h-100 rounded-lg">
              <v-img :src="recipe.image_url || 'https://placehold.co/400x300/E0F2F7/00695C?text=No+Image'" height="180px" cover />
              <v-card-title class="text-truncate">{{ recipe.name }}</v-card-title>
              <v-card-subtitle class="pb-3 text-teal">
                {{ recipe.cuisine?.name || 'Various' }} | {{ recipe.category?.name || 'Recipe' }}
              </v-card-subtitle>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: "CreatorProfileView",
  data() {
    return {
      recipes: [],
      loading: false,
      error: null,
      creatorName: ''
    }
  },
  mounted() {
    this.fetchCreatorRecipes()
  },
  methods: {
    async fetchCreatorRecipes() {
      const creatorId = this.$route.params.id;
      this.loading = true;
      
      try {
        const res = await fetch(`http://127.0.0.1:8000/recipe/creator/${creatorId}`);
        if (!res.ok) throw new Error("Failed to load recipes.");
        
        this.recipes = await res.json();
        
        if (this.recipes.length > 0) {
          this.creatorName = this.recipes[0].creator?.full_name || 'Anonymous';
        } else {
          this.creatorName = 'Creator';
        }
      } catch (e) {
        console.error(e);
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>