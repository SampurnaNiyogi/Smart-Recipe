<template>
  <v-app-bar app color="green darken-2" dark>
    <v-toolbar-title>Recipe Manager</v-toolbar-title>
    <v-spacer></v-spacer>
    <v-btn text to="/" tag="router-link">Home</v-btn>
    <v-btn text to="/chatbot" tag="router-link">ChatBot</v-btn>
    <v-btn text to="/add" tag="router-link">Add Recipe</v-btn>
    <v-btn icon to="/profile" tag="router-link">
      <v-icon>mdi-robot</v-icon>
    </v-btn>
    <v-btn icon to="/profile" tag="router-link">
      <v-icon>mdi-account-circle</v-icon>
    </v-btn>
  </v-app-bar>
</template>
