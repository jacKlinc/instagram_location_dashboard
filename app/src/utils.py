from dataclasses import dataclass
from abc import ABC, abstractmethod

import streamlit as st


class Page(ABC):
    @abstractmethod
    def write(self):
        pass


def add_custom_css():
    st.markdown(
        """
        <style>
        </style>
        """,
        unsafe_allow_html=True,
    )
