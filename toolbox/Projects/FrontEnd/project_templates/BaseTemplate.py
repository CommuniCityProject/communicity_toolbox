import streamlit as st


class BaseTemplate:

    def __init__(self, name: str, port: int,template, **kwargs):
        self.name = name
        self.port = port
    
    def __call__(self):
        st.title(self.name)
    