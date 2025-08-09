<template>
  <v-app>
    <v-main>
      <v-container>
        <!-- Main Greeting -->
        <v-row class="mt-10">
          <v-col>
            <h2>Hi {{ user }}!!</h2>
            <p>Welcome to your personal recipe manager.....</p>
          </v-col>
        </v-row>

        <!-- Search & Recently Viewed -->
        <v-row class="mt-4">
          <v-col cols="12" md="6">
            <v-text-field
              v-model="search"
              label="Search"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              dense
            />
          </v-col>
          <v-col cols="12" md="6" class="text-right">
            <v-card flat class="pa-2 grey lighten-4 text-center">
              <strong>Recently Viewed...</strong>
            </v-card>
          </v-col>
        </v-row>

        <!-- Your Recipes -->
        <v-row class="mt-8">
          <v-col cols="12">
            <h3>Your Recipes......</h3>
          </v-col>

          <v-col cols="6" md="3" v-for="(recipe, i) in recipes" :key="i">
            <v-card>
              <v-img :src="recipe.image" height="150px" />
              <v-card-title>{{ recipe.name }}</v-card-title>
            </v-card>
          </v-col>
        </v-row>

        <!-- Go to Recipes Button -->
        <v-row justify="end" class="mt-4">
          <v-btn color="black" dark @click="$router.push('/recipes')">
            Go to Recipes
            <v-icon end>mdi-arrow-right</v-icon>
          </v-btn>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: 'DashboardView',
  data() {
    return {
      user: 'User',
      search: '',
      recipes: [
        {
          name: 'Pancakes',
          image: 'https://images.unsplash.com/photo-1589307004391-91c91b4ef454?auto=format&fit=crop&w=300&q=80'
        },
        {
          name: 'Chicken Curry',
          image: 'https://images.unsplash.com/photo-1627308595229-7830a5c91f9f?auto=format&fit=crop&w=300&q=80'
        },
        {
          name: 'Image from file',
          image: 'https://via.placeholder.com/300x200?text=Image+from+file'
        },
        {
          name: 'Image from file',
          image: 'https://via.placeholder.com/300x200?text=Image+from+file'
        }
      ]
    }
  },
  methods: {
    goToRecipes() {
      alert('Redirecting to full recipe list...')
      // You can use this.$router.push('/recipes') if a route is defined
    },
    goHome() {
      this.$router.push('/')
    }
  }
}
</script>
