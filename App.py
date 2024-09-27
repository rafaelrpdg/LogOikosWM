import streamlit as st
from utils.Authentication import Authenticator

class Application:
    def __init__(self):
        self.authenticator = Authenticator()

    def run(self):
        # Exibe a página de login e autentica o usuário
        user_role = self.authenticator.authenticate_user()
        
        # Direciona para as páginas dependendo do papel do usuário
        if user_role == "admin":
            st.experimental_set_query_params(page="admin")
            from pages.AdminPage import AdminPage
            AdminPage().run()
        elif user_role == "user":
            st.experimental_set_query_params(page="user")
            from pages.UserPage import UserPage
            UserPage().run()
        else:
            st.warning("Usuário não autenticado.")
            from pages.Logon import LogonPage
            LogonPage().run()

if __name__ == "__main__":
    app = Application()
    app.run()
