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
            Created by: 
            <router-link 
              v-if="recipe.creator" 
              :to="`/creator/${recipe.creator._id || recipe.creator.uuid}`" 
              class="text-decoration-none text-teal font-weight-bold"
            >
              {{ recipe.creator.user_name }}
            </router-link>
            <span v-else>Anonymous</span>
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

            <v-divider class="my-8"></v-divider>
            <h3 class="text-h6 mb-4 font-weight-bold text-teal-darken-3">
              <v-icon start color="teal">mdi-comment-multiple-outline</v-icon>
              Comments
            </h3>
            
            <div v-if="comments && comments.length > 0" class="mb-4">
              <v-card v-for="comment in comments" :key="comment._id" class="mb-4 pa-4 bg-grey-lighten-4" elevation="0" border>
                <div class="d-flex align-start">
                  <v-avatar color="teal-darken-1" size="40" class="text-white font-weight-bold mr-3 mt-1">
                    {{ comment.user_name.charAt(0).toUpperCase() }}
                  </v-avatar>
                  <div class="flex-grow-1">
                    <div class="d-flex justify-space-between align-center">
                      <span class="font-weight-bold">{{ comment.user_name }}</span>
                      <span class="text-caption text-grey">{{ new Date(comment.created_at).toLocaleString() }}</span>
                    </div>
                    <p class="text-body-1 mt-1 mb-2" style="opacity: 0.85; white-space: pre-wrap;">{{ comment.text }}</p>

                    <v-btn size="small" variant="text" color="teal" density="compact" class="px-0" @click="toggleReply(comment._id)">
                      <v-icon start size="small">mdi-reply</v-icon> Reply
                    </v-btn>

                    <div v-if="comment.replies && comment.replies.length > 0" class="mt-3 pl-2 pl-sm-4 border-s-sm border-teal-lighten-4">
                      <div v-for="reply in comment.replies" :key="reply.id" class="d-flex align-start mt-3 pt-3 border-t">
                        <v-avatar color="blue-grey-lighten-4" size="32" class="text-blue-grey-darken-3 font-weight-bold mr-3 mt-1">
                          {{ reply.user_name.charAt(0).toUpperCase() }}
                        </v-avatar>
                        <div class="flex-grow-1">
                          <div class="d-flex justify-space-between align-center">
                            <span class="font-weight-bold text-subtitle-2">{{ reply.user_name }}</span>
                            <span class="text-caption text-grey">{{ new Date(reply.created_at).toLocaleString() }}</span>
                          </div>
                          <p class="text-body-2 mt-1" style="opacity: 0.85; white-space: pre-wrap;">{{ reply.text }}</p>
                        </div>
                      </div>
                    </div>

                    <div v-if="activeReplyId === comment._id" class="mt-4">
                      <v-textarea
                        v-model="replyText"
                        label="Write a reply..."
                        variant="outlined"
                        rows="1"
                        auto-grow
                        density="compact"
                        hide-details
                        class="mb-2 bg-white"
                        :disabled="submittingReply"
                      ></v-textarea>
                      <div class="d-flex justify-end gap-2">
                        <v-btn size="small" variant="text" color="grey-darken-1" @click="activeReplyId = null" :disabled="submittingReply">Cancel</v-btn>
                        <v-btn size="small" color="teal" @click="submitReply(comment._id)" :loading="submittingReply" :disabled="!replyText.trim()">Post Reply</v-btn>
                      </div>
                    </div>

                  </div>
                </div>
              </v-card>
            </div>
            <p v-else class="text-grey mb-4 font-italic">No comments yet. Be the first to share your thoughts!</p>

            <v-form @submit.prevent="submitComment">
              <v-textarea
                v-model="newCommentText"
                label="Add a comment..."
                variant="outlined"
                rows="2"
                auto-grow
                :disabled="submittingComment"
              ></v-textarea>
              <div class="d-flex justify-end">
                <v-btn color="teal" type="submit" :loading="submittingComment" :disabled="!newCommentText.trim()" prepend-icon="mdi-send">
                  Post
                </v-btn>
              </div>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="substituteDialog" max-width="400">
      <v-card>
        <v-card-title>Substitutes for "{{ selectedIngredient }}"</v-card-title>
        <v-card-text>
          <v-list v-if="substitutes.length > 0">
            <v-list-item v-for="(sub, i) in substitutes" :key="i" :title="sub"></v-list-item>
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
      comments: [],
      loading: false,
      error: "",
      substituteDialog: false, 
      selectedIngredient: '', 
      substitutes: [],
      currentUserUuid: null,
      
      // Comment & Reply states
      newCommentText: '',
      submittingComment: false,
      activeReplyId: null,
      replyText: '',
      submittingReply: false
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
      this.comments = []
      this.newCommentText = ''
      this.activeReplyId = null
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
        this.fetchSimilarRecipes(id)
        this.fetchComments(id)
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
    async fetchComments(id) {
      try {
        const res = await fetch(`http://127.0.0.1:8000/recipe/${id}/comments`);
        if (res.ok) {
          this.comments = await res.json();
        }
      } catch (e) {
        console.error("Could not fetch comments:", e);
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
    },
    
    // Primary Commenting
    async submitComment() {
      if (!this.newCommentText.trim()) return;
      this.submittingComment = true;
      
      const authStore = useAuthStore();
      const token = authStore.token;
      
      if (!token) {
        alert("You must be logged in to comment.");
        this.$router.push('/login');
        return;
      }

      try {
        const res = await fetch(`http://127.0.0.1:8000/recipe/${this.recipe._id}/comment`, {
          method: 'POST',
          headers: { 
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ text: this.newCommentText })
        });
        
        if (res.ok) {
          const data = await res.json();
          this.comments.push(data.comment);
          this.newCommentText = ''; 
        } else {
          const errorData = await res.json();
          alert(`Failed to post comment: ${errorData.detail || 'Unknown error'}`);
        }
      } catch (e) {
        console.error(e);
      } finally {
        this.submittingComment = false;
      }
    },

    // Threaded Replies
    toggleReply(commentId) {
      if (this.activeReplyId === commentId) {
        this.activeReplyId = null;
        this.replyText = '';
      } else {
        this.activeReplyId = commentId;
        this.replyText = '';
      }
    },
    async submitReply(commentId) {
      if (!this.replyText.trim()) return;
      this.submittingReply = true;

      const authStore = useAuthStore();
      const token = authStore.token;

      if (!token) {
        alert("You must be logged in to reply.");
        this.$router.push('/login');
        return;
      }

      try {
        const res = await fetch(`http://127.0.0.1:8000/recipe/${this.recipe._id}/comment/${commentId}/reply`, {
          method: 'POST',
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ text: this.replyText })
        });

        if (res.ok) {
          const data = await res.json();
          
          const targetComment = this.comments.find(c => c._id === commentId);
          if (targetComment) {
            if (!targetComment.replies) targetComment.replies = [];
            targetComment.replies.push(data.reply);
          }
          
          this.activeReplyId = null;
          this.replyText = '';
        } else {
          const errorData = await res.json();
          alert(`Failed to post reply: ${errorData.detail || 'Unknown error'}`);
        }
      } catch (e) {
        console.error(e);
      } finally {
        this.submittingReply = false;
      }
    }
  }
}
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}
</style>