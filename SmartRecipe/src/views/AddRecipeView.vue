<template>
  <v-app>
    <v-main>
      <v-container>
        <v-card class="pa-6 mt-8" outlined>
          <v-card-title>Add/Edit your recipes</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field label="Recipe Name" v-model="form.name" />
                <v-text-field label="Add Description" v-model="form.description" />

                <v-text-field
                  label="Add Ingredient"
                  v-model="newIngredient"
                  append-inner-icon="mdi-plus"
                  @click:append-inner="addIngredient"
                />

                <v-row>
                  <v-col cols="6">
                    <v-text-field label="Quantity" v-model="form.quantity" />
                  </v-col>
                  <v-col cols="6">
                    <v-text-field label="Unit" v-model="form.unit" />
                  </v-col>
                </v-row>

                <v-btn variant="tonal" @click="addIngredient">+ Add Ingredient</v-btn>
              </v-col>

              <v-col cols="12" md="6">
                <v-file-input
                  label="Upload Image"
                  accept="image/*"
                  v-model="form.image"
                  prepend-icon="mdi-upload"
                />

                <v-select
                  :items="categories"
                  label="Choose category"
                  v-model="form.category"
                  item-title="name"
                  item-value="_id"
                />

                <v-select
                  :items="cuisines"
                  label="Choose cuisine"
                  v-model="form.cuisine"
                  item-title="name"
                  item-value="_id"
                />
                <v-select 
                  :items="diets"
                  label="Choose diets"
                  v-model="form.diets"
                  item-title="name"
                  item-value="_id"
                />
              </v-col>
            </v-row>

            <v-btn color="pink darken-1" class="mt-4" @click="submitRecipe">Submit</v-btn>
          </v-card-text>
        </v-card>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
export default {
  data() {
    return {
      cuisines: [],
      categories: [],
      diets: [],
      form: {
        name: '',
        description: '',
        ingredients: [],
        quantity: '',
        unit: '',
        category: '',
        cuisine: '',
        image: null
      },
      newIngredient: '',
      selectedCuisine: null,
      selectedCategory: null,
      selectedDiet: null
    }
  },
  mounted() {
    this.fetchCuisines();
    this.fetchCategories();
    this.fetchDiets();
  },
  methods: {
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
    addIngredient() {
      if (this.newIngredient) {
        this.form.ingredients.push(this.newIngredient)
        this.newIngredient = ''
      }
    },
    submitRecipe() {
      console.log('Recipe Submitted:', this.form)
      alert('Recipe Submitted!')
    }
  }
}
</script>
