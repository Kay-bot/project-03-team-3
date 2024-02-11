import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

def authenticate():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        username = st.text_input("Username:")
        password = st.text_input("Password:", type="password")

        # Load valid credentials from environment variables
        valid_credentials = {
            "NDIA": {"username": os.getenv("NDIA_USERNAME"), "password": os.getenv("NDIA_PASSWORD")},
            "Participant": {"username": os.getenv("PARTICIPANT_USERNAME"), "password": os.getenv("PARTICIPANT_PASSWORD")},
            "ServiceProvider": {"username": os.getenv("SERVICE_PROVIDER_USERNAME"), "password": os.getenv("SERVICE_PROVIDER_PASSWORD")}
        }

        for role, credentials in valid_credentials.items():
            if username == credentials["username"] and password == credentials["password"]:
                st.session_state.authenticated = True
                st.success(f"{role} authentication successful!")
                return role

        st.error("Authentication failed. Please try again.")
        return None