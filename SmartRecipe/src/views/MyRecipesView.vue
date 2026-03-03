<template>
  <v-container>
    <v-row class="mt-8">
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-6">
          <h2 class="text-h4">My Recipes</h2>
          <v-btn color="teal" prepend-icon="mdi-plus" @click="$router.push('/add')">Create New</v-btn>
        </div>

        <v-alert v-if="error" type="error" outlined class="mb-4">{{ error }}</v-alert>

        <v-row v-if="loading">
          <v-col v-for="n in 4" :key="n" cols="12" sm="6" md="4" lg="3">
            <v-skeleton-loader type="card"></v-skeleton-loader>
          </v-col>
        </v-row>

        <v-row v-else-if="recipes.length === 0">
          <v-col cols="12">
            <v-card class="text-center pa-10" outlined>
              <v-icon size="64" color="grey lighten-1">mdi-silverware-fork-knife</v-icon>
              <h3 class="text-h6 mt-4 text-grey-darken-1">You haven't created any recipes yet.</h3>
              <v-btn color="teal" class="mt-4" @click="$router.push('/add')">Add Your First Recipe</v-btn>
            </v-card>
          </v-col>
        </v-row>

        <v-row v-else>
          <v-col cols="12" sm="6" md="4" lg="3" v-for="recipe in recipes" :key="recipe._id">
            <v-card @click="$router.push(`/recipe/details/${recipe._id}`)" hover>
              <v-img :src="recipe.image_url || 'https://placehold.co/400x300/E0F2F7/00695C?text=No+Image'" height="180px" cover />
              <v-card-title class="text-truncate">{{ recipe.name }}</v-card-title>
              <v-card-subtitle>
                {{ recipe.cuisine?.name || 'N/A' }} | {{ recipe.category?.name || 'N/A' }}
              </v-card-subtitle>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn variant="text" color="teal" prepend-icon="mdi-pencil" @click.stop="$router.push(`/edit/${recipe._id}`)">Edit</v-btn>
                <v-btn variant="text" color="error" prepend-icon="mdi-delete" @click.stop="confirmDelete(recipe)">Delete</v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
    </v-row>

    <v-dialog v-model="deleteDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6">Delete Recipe?</v-card-title>
        <v-card-text>Are you sure you want to delete "{{ recipeToDelete?.name }}"? This action cannot be undone.</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey-darken-1" variant="text" @click="deleteDialog = false">Cancel</v-btn>
          <v-btn color="error" variant="text" @click="deleteRecipe" :loading="deleting">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-container>
</template>

<script>
import { useAuthStore } from '../stores/auth'

export default {
  name: "MyRecipesView",
  data() {
    return {
      recipes: [],
      loading: false,
      error: null,
      deleteDialog: false,
      recipeToDelete: null,
      deleting: false
    }
  },
  mounted() {
    this.fetchMyRecipes()
  },
  methods: {
    async fetchMyRecipes() {
      const authStore = useAuthStore()
      const token = authStore.token

      if (!token) {
        this.$router.push('/login')
        return
      }

      this.loading = true
      this.error = null

      try {
        const res = await fetch("http://127.0.0.1:8000/my-recipes", {
          headers: { "Authorization": `Bearer ${token}` }
        })

        if (res.status === 401 || res.status === 403) {
          authStore.logout()
          this.$router.push('/login')
          return
        }

        if (!res.ok) throw new Error("Failed to load your recipes.")
        
        this.recipes = await res.json()
      } catch (e) {
        console.error(e)
        this.error = e.message
      } finally {
        this.loading = false
      }
    },
    confirmDelete(recipe) {
      this.recipeToDelete = recipe
      this.deleteDialog = true
    },
    async deleteRecipe() {
      if (!this.recipeToDelete) return
      
      this.deleting = true
      const authStore = useAuthStore()
      
      try {
        const res = await fetch(`http://127.0.0.1:8000/recipe/${this.recipeToDelete._id}`, {
          method: 'DELETE',
          headers: { "Authorization": `Bearer ${authStore.token}` }
        })
        
        if (!res.ok) {
          const data = await res.json()
          throw new Error(data.detail || "Failed to delete recipe")
        }
        
        this.recipes = this.recipes.filter(r => r._id !== this.recipeToDelete._id)
        this.deleteDialog = false
        this.recipeToDelete = null
        
      } catch (e) {
        alert(e.message)
      } finally {
        this.deleting = false
      }
    }
  }
}
</script>