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
                Description: {{ recipe.description }}<br />
                Cuisine : {{ recipe.cuisine_id }}<br />
                Category: {{ recipe.category_id}}<br />
                Diet: {{ recipe.diet_id }}<br />
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
      const id = this.$route.params.id; // get id from the route
      if (!id) { this.error = "Missing recipe id in route."; return; }
      this.loading = true;
      this.error = "";
      try {
        const res = await fetch(`http://127.0.0.1:8000/recipe/${id}`); // valid URL
        if (!res.ok) throw new Error(`Fetch failed (${res.status})`);
        this.recipe = await res.json();
      } catch (e) {
        this.error = e.message || "Error fetching recipe.";
        this.recipe = {};
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
