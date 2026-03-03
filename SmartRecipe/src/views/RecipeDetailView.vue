<template>
  <v-container>
    <v-row class="mt-8">
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-4">
          <v-btn variant="text" @click="$router.back()">← Back to Recipes</v-btn>
          <v-btn v-if="canEdit" color="teal" @click="$router.push(`/edit/${recipe._id}`)">Edit Recipe</v-btn>
        </div>
        <v-card :loading="loading">
          <v-img :src="recipe.image_url || 'https://placehold.co/1200x400/E0F2F7/00695C?text=No+Image'" height="300px" cover />
          
          <v-card-title class="text-h5 mt-2">{{ recipe.name }}</v-card-title>
          
          <v-card-subtitle class="text-subtitle-1 font-weight-medium text-teal-darken-3">
            Created by: {{ recipe.creator?.user_name || 'Anonymous' }}
          </v-card-subtitle>
          
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
  </v-container>
</template>

<script>
import { useAuthStore } from '../stores/auth'

export default {
  name: "RecipeDetailView",
  data() {
    return {
      recipe: {},
      similarRecipes: [],
      loading: false,
      error: "",
      substituteDialog: false, 
      selectedIngredient: '', 
      substitutes: [],
      currentUserUuid: null
    }
  },
  mounted() {
    this.fetchDataForRecipe()
    this.fetchCurrentUser()
  },
  watch: {
    "$route.params.id"() {
      this.recipe = {}
      this.similarRecipes = []
      this.fetchDataForRecipe()
    }
  },
  computed: {
    ingredientList() {
      if (!this.recipe.ingredients) return []
      return this.recipe.ingredients.split(',').map(item => item.trim())
    },
    canEdit() {
      if (!this.recipe.creator || !this.currentUserUuid) return false
      return this.recipe.creator.uuid === this.currentUserUuid
    }
  },
  methods: {
    async fetchCurrentUser() {
      const authStore = useAuthStore()
      const token = authStore.token
      if (!token) return
      try {
        const res = await fetch("http://127.0.0.1:8000/users/me", {
          headers: { "Authorization": `Bearer ${token}` }
        })
        if (res.ok) {
          const data = await res.json()
          this.currentUserUuid = data.uuid
        }
      } catch (e) {
        console.error(e)
      }
    },
    async fetchDataForRecipe() {
      const id = this.$route.params.id
      if (!id) return
      
      await this.fetchRecipe(id)
      if (this.recipe && this.recipe._id) {
        await this.fetchSimilarRecipes(id)
      }
    },
    async fetchRecipe(id) {
      const authStore = useAuthStore()
      const token = authStore.token
      if (!token) {
        this.error = "Authentication error."
        this.$router.push('/login')
        return
      }

      this.loading = true
      this.error = ""
      try {
        const res = await fetch(`http://127.0.0.1:8000/recipe/${id}`, {
           headers: { "Authorization": `Bearer ${token}` }
        })
        if (res.status === 401) { 
          authStore.logout()
          this.$router.push('/login')
          throw new Error('Unauthorized') 
        }
        if (!res.ok) throw new Error(`Fetch failed (${res.status})`)
        this.recipe = await res.json()
      } catch (e) {
        if (e.message !== 'Unauthorized') this.error = e.message || "Error fetching recipe details."
      } finally {
        this.loading = false
      }
    },
    async fetchSimilarRecipes(id) {
      const authStore = useAuthStore()
      const token = authStore.token
      if (!token) return

      try {
        const res = await fetch(`http://127.0.0.1:8000/recommendations/similar/${id}`, {
           headers: { "Authorization": `Bearer ${token}` }
        })
        if (res.status === 401) return
        if (!res.ok) throw new Error(`Failed to fetch similar recipes (${res.status})`)
        this.similarRecipes = await res.json()
      } catch (e) {
        console.error(e.message)
      }
    },
    async findSubstitutes(ingredient) {
      const cleanIngredient = ingredient
        .replace(/[\d/]+( cup| tbsp| tsp| tablespoon| teaspoon)?s?/i, '')
        .replace(/\(.*\)/, '')
        .trim()
        
      if (!cleanIngredient) return

      this.selectedIngredient = ingredient
      this.substitutes = []
      this.substituteDialog = true
      
      const authStore = useAuthStore()
      const token = authStore.token
      if (!token) return

      try {
        const res = await fetch(`http://127.0.0.1:8000/recipe/substitutes/${cleanIngredient}`, {
           headers: { "Authorization": `Bearer ${token}` }
        })
        if (!res.ok) throw new Error("Could not fetch substitutes")
        this.substitutes = await res.json()
      } catch (e) {
        console.error(e.message)
        this.substitutes = []
      }
    }
  }
}
</script>