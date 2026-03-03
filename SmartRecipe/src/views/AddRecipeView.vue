<template>
  <v-container class="py-8">
    <v-row justify="center">
      <v-col cols="12" md="10" lg="8">
        <v-card class="pa-6 rounded-lg" elevation="3">
          <v-card-title class="text-h4 font-weight-bold text-teal-darken-3 mb-6 d-flex align-center">
            <v-icon start color="teal" size="large" class="mr-3">
              {{ isEditMode ? 'mdi-pencil-circle' : 'mdi-plus-circle' }}
            </v-icon>
            {{ isEditMode ? 'Edit Recipe' : 'Create New Recipe' }}
          </v-card-title>

          <v-card-text>
            <v-form @submit.prevent="submitRecipe">
              <h3 class="text-h6 font-weight-medium mb-4 text-grey-darken-2">Basic Information</h3>
              <v-row>
                <v-col cols="12">
                  <v-text-field
                    label="Recipe Name"
                    v-model="form.name"
                    variant="outlined"
                    prepend-inner-icon="mdi-silverware-fork-knife"
                    required
                  ></v-text-field>
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    label="Short Description"
                    v-model="form.description"
                    variant="outlined"
                    prepend-inner-icon="mdi-text-short"
                  ></v-text-field>
                </v-col>
              </v-row>

              <v-divider class="my-6"></v-divider>

              <h3 class="text-h6 font-weight-medium mb-4 text-grey-darken-2">Ingredients & Instructions</h3>
              <v-row>
                <v-col cols="12">
                  <v-textarea
                    label="Ingredients (comma separated)"
                    v-model="form.ingredients"
                    variant="outlined"
                    prepend-inner-icon="mdi-format-list-bulleted"
                    rows="3"
                    auto-grow
                  ></v-textarea>
                </v-col>
                <v-col cols="12">
                  <v-textarea
                    label="Step-by-step Instructions"
                    v-model="form.instructions"
                    variant="outlined"
                    prepend-inner-icon="mdi-chef-hat"
                    rows="5"
                    auto-grow
                  ></v-textarea>
                </v-col>
              </v-row>

              <v-divider class="my-6"></v-divider>

              <h3 class="text-h6 font-weight-medium mb-4 text-grey-darken-2">Categorization & Media</h3>
              <v-row>
                <v-col cols="12" md="6">
                  <v-select
                    :items="categories"
                    label="Category"
                    v-model="form.category_id"
                    item-title="name"
                    item-value="_id"
                    variant="outlined"
                    prepend-inner-icon="mdi-shape"
                  ></v-select>
                </v-col>
                <v-col cols="12" md="6">
                  <v-select
                    :items="cuisines"
                    label="Cuisine"
                    v-model="form.cuisine_id"
                    item-title="name"
                    item-value="_id"
                    variant="outlined"
                    prepend-inner-icon="mdi-earth"
                  ></v-select>
                </v-col>
                <v-col cols="12" md="6">
                  <v-select
                    :items="diets"
                    label="Dietary Preference"
                    v-model="form.diet_id"
                    item-title="name"
                    item-value="_id"
                    variant="outlined"
                    prepend-inner-icon="mdi-leaf"
                  ></v-select>
                </v-col>
                <v-col cols="12" md="6">
                  <v-file-input
                    label="Upload Recipe Image"
                    v-model="imageFile"
                    accept="image/*"
                    prepend-inner-icon="mdi-camera"
                    prepend-icon=""
                    variant="outlined"
                    show-size
                  ></v-file-input>
                </v-col>

                <v-col cols="12" v-if="form.image_url && !imageFile" class="d-flex justify-center">
                  <v-img
                    :src="form.image_url"
                    max-height="200"
                    max-width="300"
                    class="rounded-lg elevation-2"
                    cover
                  ></v-img>
                </v-col>
              </v-row>

              <v-row class="mt-6">
                <v-col cols="12" class="d-flex gap-4">
                  <v-btn
                    variant="outlined"
                    color="grey-darken-1"
                    size="large"
                    class="flex-grow-1"
                    @click="$router.back()"
                    :disabled="isSubmitting"
                  >
                    Cancel
                  </v-btn>
                  <v-btn
                    color="teal-darken-2"
                    size="large"
                    class="flex-grow-1"
                    type="submit"
                    :loading="isSubmitting"
                    :disabled="isSubmitting"
                    prepend-icon="mdi-content-save"
                  >
                    {{ isEditMode ? 'Save Changes' : 'Publish Recipe' }}
                  </v-btn>
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { useAuthStore } from '../stores/auth'

export default {
  data() {
    return {
      cuisines: [],
      categories: [],
      diets: [],
      form: {
        name: '',
        description: '',
        ingredients: '',
        instructions: '',
        category_id: '',
        cuisine_id: '',
        diet_id: '',
        image_url: '',
      },
      imageFile: null,
      isEditMode: false,
      recipeId: null,
      isSubmitting: false
    }
  },
  mounted() {
    this.fetchCuisines()
    this.fetchCategories()
    this.fetchDiets()

    if (this.$route.params.id) {
      this.isEditMode = true
      this.recipeId = this.$route.params.id
      this.loadRecipeDetails()
    }
  },
  methods: {
    async loadRecipeDetails() {
      const authStore = useAuthStore()
      try {
        const res = await fetch(`http://127.0.0.1:8000/recipe/${this.recipeId}`, {
          headers: { "Authorization": `Bearer ${authStore.token}` }
        })
        if (res.ok) {
          const data = await res.json()
          this.form = {
            name: data.name,
            description: data.description,
            ingredients: data.ingredients,
            instructions: data.instructions,
            category_id: data.category?._id || data.category,
            cuisine_id: data.cuisine?._id || data.cuisine,
            diet_id: data.diet?._id || data.diet,
            image_url: data.image_url || ''
          }
        }
      } catch (e) {
        console.error(e)
      }
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
    async uploadImageToCloudinary() {
      const fileToUpload = Array.isArray(this.imageFile) ? this.imageFile[0] : this.imageFile
      
      const formData = new FormData()
      formData.append('file', fileToUpload)
      formData.append('upload_preset', 'ForSmartRecipe')
      formData.append('cloud_name', 'djw8w0yxl')

      const res = await fetch(`https://api.cloudinary.com/v1_1/djw8w0yxl/image/upload`, {
        method: 'POST',
        body: formData
      })
      
      if (!res.ok) throw new Error("Image upload failed")
      
      const data = await res.json()
      return data.secure_url
    },
    async submitRecipe() {
      const authStore = useAuthStore()
      const token = authStore.token

      if (!token) {
        alert("Authentication error: You are not logged in.")
        this.$router.push('/login')
        return
      }

      this.isSubmitting = true

      try {
        if (this.imageFile) {
          this.form.image_url = await this.uploadImageToCloudinary()
        }

        const url = this.isEditMode 
          ? `http://127.0.0.1:8000/recipe/${this.recipeId}` 
          : "http://127.0.0.1:8000/create_recipe"
        const method = this.isEditMode ? "PUT" : "POST"

        const response = await fetch(url, {
          method: method,
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
          },
          body: JSON.stringify(this.form)
        })

        if (response.status === 401 || response.status === 403) {
           alert("Authentication failed. Please log in again.")
           authStore.logout()
           this.$router.push('/login')
           return
        }

        if (!response.ok) {
          const errorData = await response.json()
          alert(`Error saving recipe: ${errorData.detail || response.statusText}`)
          return
        }

        this.$router.push('/my-recipes')

      } catch (err) {
        alert(`Something went wrong while saving the recipe: ${err.message}`)
      } finally {
        this.isSubmitting = false
      }
    }
  }
}
</script>

<style scoped>
.gap-4 {
  gap: 16px;
}
</style>