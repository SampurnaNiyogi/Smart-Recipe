// src/firebase.js
import { initializeApp } from 'firebase/app'
import { getAuth } from 'firebase/auth'

const firebaseConfig = {
  apiKey: "AIzaSyBBBLyqA6fIx77nsbWXcWcJ02Kr-1jXDEo",
  authDomain: "connectsql-4038567f.firebaseapp.com",
  projectId: "connectsql-4038567f",
  storageBucket: "connectsql-4038567f.firebasestorage.app",
  messagingSenderId: "25636121990",
  appId: "1:25636121990:web:e8ec394ce0b7d4705a9007"
}

const app = initializeApp(firebaseConfig)
const auth = getAuth(app)

export { auth }
