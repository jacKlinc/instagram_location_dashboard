import streamlit as st
import pandas as pd

from ..utils import Page, get_instagram_locations, plot_coords


class InstagramSearch(Page):
    def __init__(self, state):
        self.state = state

    def write(self):
        st.title("Instagram Search")
        st.text(
            "This section will use the existing Bellingcat repo to search for activity in an area"
        )

        # TODO: add regex to for check correct format
        cookies = st.text_input("Please enter your Instagram cookies", type="password")

        # TODO: add regex to for check correct format
        latitude = st.text_input("Please enter the latitude", placeholder=52.3676)  # type: ignore
        longitude = st.text_input("Please enter the longitude", placeholder=4.9041)  # type: ignore

        if cookies:
            locations = get_instagram_locations(latitude, longitude, cookies)
            if locations:
                locations_df = pd.DataFrame(locations)
                st.write(locations_df)
                plot_coords(locations_df)
            else:
                st.text("No results found. Please check inputs again")
