# 🍳 SmartRecipe — AI-Powered Recipe Management Platform

> A full-stack, intelligent recipe management web application built with **FastAPI**, **MongoDB (Beanie)**, and **Vue.js**.  
> SmartRecipe lets users discover, create, and manage recipes — powered by **AI-based recommendations**, **seasonal suggestions**, and an **interactive cooking chatbot**.

---

## 🌟 Overview

**SmartRecipe** transforms the way people explore food.  
Users can securely log in using **OTP-based authentication**, browse recipes, filter by cuisine or diet, and even chat with an AI bot to get personalized cooking tips, ingredient substitutes, or seasonal dish suggestions.

The application combines:
- 🧠 **AI recommendations** (TF-IDF + Cosine Similarity)
- 🔐 **Secure JWT authentication**
- 💬 **Interactive chatbot assistance**
- 🎨 **Modern Vue.js UI with Vuetify**

---

## 🚀 Features

### 🔐 Authentication & Security
- Password-free **OTP-based phone login**
- **JWT token** authentication for session security
- Frontend and backend route protection
- Profile view via secure `/users/me` endpoint

### 🍲 Recipe Management (CRUD)
- Add new recipes linked to **Cuisine**, **Category**, and **Diet**
- View all recipes as cards with images and descriptions
- Single recipe page showing ingredients and cooking steps
- MongoDB document relationships handled by **Beanie ODM**

### 🔍 Search & Filters
- **Faceted filtering** by cuisine, category, or diet
- **Full-text search** on recipe names, ingredients, and descriptions

### 👤 User Personalization
- Dynamic greetings like “Welcome back, {username}!”
- User profile with phone, name, and email
- **View history tracking** with timestamps

### 🧠 AI-Based Recommendations
- **Content-based filtering** using TF-IDF + cosine similarity
- **Cached model** for fast retrieval of similar recipes
- **Seasonal suggestions** (e.g., soups in winter, salads in summer)

### 💬 Smart Chatbot
- Integrated chatbot with **rule-based intent detection**
- Handles:
  - Recipe search queries (“How to make pasta?”)
  - Ingredient substitutes (“Substitute for butter”)
  - Seasonal dish suggestions
  - Friendly greetings
- Ingredient chips on recipe pages open a dialog showing substitutes

---

## 🧱 Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | Vue.js, Vuetify, Pinia |
| **Backend** | FastAPI (Python) |
| **Database** | MongoDB + Beanie ODM |
| **Machine Learning** | scikit-learn (TF-IDF, cosine similarity) |
| **Auth & Security** | JWT, Phone-based OTP |
| **State Management** | Pinia |
| **Hosting (optional)** | Render / Vercel / MongoDB Atlas |

---

## ⚙️ Installation & Setup

### 🖥️ 1️⃣ Clone the Repository
```bash
git clone [https://github.com/Sampurna/SmartRecipe.git](https://github.com/SampurnaNiyogi/Smart-Recipe)
cd SmartRecipe
```
### 🧩 2️⃣ Backend Setup   
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
### 💻 3️⃣ Frontend Setup
```bash
cd SmartRecipe
npm install
npm run server
```

