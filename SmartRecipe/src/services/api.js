import axios from 'axios'

const API = axios.create({
  baseURL: 'http://localhost:8000/recipes', // or your deployed URL
})

export default {
  getAllRecipes: () => API.get('/'),
  getRecipe: (id) => API.get(`/${id}`),
  addRecipe: (recipe) => API.post('/', recipe),
  updateRecipe: (id, recipe) => API.put(`/${id}`, recipe),
  deleteRecipe: (id) => API.delete(`/${id}`),
}
