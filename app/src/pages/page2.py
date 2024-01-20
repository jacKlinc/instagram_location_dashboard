import streamlit as st
from ..utils import Page


class Page2(Page):
    def __init__(self, state):
        self.state = state

    def write(self):
        st.title("Page 2")
        slider_value = st.slider(
            "Set Value from here See it on Page 1",
            value=self.state.client_config["slider_value"],
        )
        self.state.client_config["slider_value"] = slider_value
