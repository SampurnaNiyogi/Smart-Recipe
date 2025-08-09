// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue' // Your Home/Dashboard view
import LoginView from '../views/LoginView.vue' // Your Login view
import RecipeListView from '@/views/RecipeListView.vue'
import AddRecipeView from '@/views/AddRecipeView.vue'
import ProfileView from '@/views/ProfileView.vue'
import ChatbotView from '@/views/ChatbotView.vue'
import RecipeDetailView from '@/views/RecipeDetailView.vue'
import { useAuthStore } from '../stores/auth'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/', // Set HomeView as the default route
      name: 'home',
      component: HomeView
    },
    {
      path: '/login', // Route for the login page
      name: 'login',
      component: LoginView
    },
    {
      path: '/signup', // Route for signup (can point to LoginView for now or a separate component) [cite: 33]
      name: 'signup',
      component: LoginView // Reusing LoginView as it has a "Sign Up" link/button
    },
    {
      path: '/forgot-password', // Placeholder route for forgot password [cite: 36]
      name: 'forgot-password',
      component: LoginView // Reusing LoginView for simplicity for now
    },
    {
      path: '/recipes',
      name: 'recipe',
      component: RecipeListView, 
      meta: { requiresAuth: true } 
    },
    {
      path: '/add',
      name: 'add',
      component: AddRecipeView, 
      meta: { requiresAuth: true } 
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView, 
      meta: { requiresAuth: true } 
    },
    {
      path: '/chatbot',
      name: 'chatbot',
      component: ChatbotView, 
      meta: { requiresAuth: true } 
    },
    {
      path: '/recipe/details/:id',
      name: 'recipe-detail',
      component: RecipeDetailView,
      props: true
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Wait for Firebase auth to initialize
  if (authStore.loading) {
    await new Promise(resolve => {
      const unwatch = authStore.$subscribe(() => {
        if (!authStore.loading) {
          resolve()
          unwatch()
        }
      })
    })
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})


export default router