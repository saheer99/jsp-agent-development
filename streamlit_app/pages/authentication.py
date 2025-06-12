from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
import hashlib
import streamlit as st

# Initialize the Azure Key Vault SecretClient
secret_auth_client = SecretClient(vault_url="https://jsp-agent-kv.vault.azure.net/", credential=DefaultAzureCredential())
stored_username = secret_auth_client.get_secret("admin-username").value
stored_password = secret_auth_client.get_secret("admin-password").value

# Secret key for hashing (should be stored securely)
SECRET_KEY = "your_secret_key"

# Function to create a hashed cookie
def create_auth_cookie(username, secret_key):
    expiration = (datetime.now() + timedelta(hours=1)).isoformat()  # Cookie expires in 1 hour
    cookie_value = f"{username}:{expiration}"
    hashed_cookie = hashlib.sha256(f"{cookie_value}:{secret_key}".encode()).hexdigest()
    return f"{cookie_value}:{hashed_cookie}"

# Function to validate the cookie
def validate_auth_cookie(cookie, secret_key):
    try:
        username, expiration, hashed_cookie = cookie.split(":")
        if datetime.fromisoformat(expiration) < datetime.now():
            return False  # Cookie expired
        expected_hash = hashlib.sha256(f"{username}:{expiration}:{secret_key}".encode()).hexdigest()
        return hashed_cookie == expected_hash
    except Exception:
        return False

# Function to handle authentication
def handle_authentication():
    # Initialize session state for page navigation
    if "current_page" not in st.session_state:
        st.session_state.current_page = "login"  # Default to the login page

    if "auth_cookie" not in st.session_state:
        st.session_state.auth_cookie = None

    # Validate the authentication cookie
    if st.session_state.auth_cookie and validate_auth_cookie(st.session_state.auth_cookie, SECRET_KEY):
        st.session_state.current_page = "JSP Summary"

    # Render the login page
    if st.session_state.current_page == "login":
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In")
            if submitted:
                if username == stored_username and password == stored_password:
                    st.session_state.auth_cookie = create_auth_cookie(username, SECRET_KEY)
                    st.session_state.current_page = "JSP Summary"
                    st.success("Login successful!")
                    st.markdown(
                        """
                        <script>
                        window.location.href = window.location.origin + "/?page=JSP%20Summary";
                        </script>
                        """,
                        unsafe_allow_html=True,
                        )  # Reload the app to show the summary page
                    st.stop()
                else:
                    st.error("Invalid username or password.")
        st.stop()