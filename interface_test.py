import streamlit as st
import requests

# Streamlit simple login/signup interface for testing the Sanic API

API_URL = "http://localhost:8000"  # Adjust to your Sanic server URL

# Define a function to register users
def register_user(username, phone, password):
    response = requests.post(
        f"{API_URL}/register",
        json={"username": username, "phone": phone, "password": password}
    )
    return response.json()

# Define a function to log in users
def login_user(phone, password):
    response = requests.post(
        f"{API_URL}/login",
        json={"phone": phone, "password": password}
    )
    return response.json()

# Streamlit App
st.title("CoffeeLeaf App - Login/Signup")

# Tabs for Signup and Login
tab = st.radio("Select an action", ("Signup", "Login"))

if tab == "Signup":
    st.header("User Registration")
    username = st.text_input("Username")
    phone = st.text_input("Phone Number")
    password = st.text_input("Password", type="password")
    
    if st.button("Register"):
        if username and phone and password:
            result = register_user(username, phone, password)
            st.json(result)
        else:
            st.error("Please fill in all fields.")

elif tab == "Login":
    st.header("User Login")
    phone = st.text_input("Phone Number")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if phone and password:
            result = login_user(phone, password)
            st.json(result)
        else:
            st.error("Please fill in all fields.")
