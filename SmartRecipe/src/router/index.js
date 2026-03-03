import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RecipeListView from '@/views/RecipeListView.vue'
import AddRecipeView from '@/views/AddRecipeView.vue'
import ProfileView from '@/views/ProfileView.vue'
import ChatbotView from '@/views/ChatbotView.vue'
import RecipeDetailView from '@/views/RecipeDetailView.vue'
import MyRecipesView from '@/views/MyRecipesView.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/signup',
      name: 'signup',
      component: LoginView
    },
    {
      path: '/forgot-password',
      name: 'forgot-password',
      component: LoginView
    },
    {
      path: '/recipes',
      name: 'recipe',
      component: RecipeListView, 
      meta: { requiresAuth: true } 
    },
    {
      path: '/my-recipes',
      name: 'my-recipes',
      component: MyRecipesView, 
      meta: { requiresAuth: true } 
    },
    {
      path: '/add',
      name: 'add',
      component: AddRecipeView, 
      meta: { requiresAuth: true } 
    },
    {
      path: '/edit/:id',
      name: 'edit',
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