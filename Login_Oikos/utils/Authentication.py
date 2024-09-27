import streamlit as st

class Authenticator:
    def __init__(self):
        self.users_db = {
            "admin": {"username": "admin", "password": "admin123"},
            "user": {"username": "user", "password": "user123"},
        }

    def authenticate_user(self):
        st.title("Tela de Login")
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")

        if st.button("Login"):
            for role, credentials in self.users_db.items():
                if username == credentials["username"] and password == credentials["password"]:
                    st.success(f"Bem-vindo, {username}!")
                    return role
            st.error("Usuário ou senha inválidos.")
            return None

        return None
