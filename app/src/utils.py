from abc import ABC, abstractmethod

import streamlit as st
import pandas as pd


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


def plot_coords(df: pd.DataFrame):
    """Plots GPS coordinates on Streamlit map

    Args:
        df (pd.DataFrame): table of latitudes and longitudes
    Only works where columns named: "lat", "lng"
    """
    # TODO: exception handling
    lat_lng = df[["lat", "lng"]].dropna()
    st.map(lat_lng, longitude="lng")  # type: ignore
