// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAlnYwnMpwYDAbYEF4jM5Au7fI1sYKzLKE",
  authDomain: "st-dbs.firebaseapp.com",
  projectId: "st-dbs",
  storageBucket: "st-dbs.firebasestorage.app",
  messagingSenderId: "1005819510745",
  appId: "1:1005819510745:web:f8ce8b7eae06b3202b23c8",
  measurementId: "G-0E0299808Y"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

export { app, analytics };
