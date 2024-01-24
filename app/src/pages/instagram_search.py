import streamlit as st
import pandas as pd

from ..utils import query_instagram, plot_coords
from ..types import Page, HttpStatus


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

        # NOTE we could get the cookies from a browser extension
        # TODO: add regex to for check correct format
        latitude = st.text_input("Please enter the latitude", placeholder=52.3676)  # type: ignore
        longitude = st.text_input("Please enter the longitude", placeholder=4.9041)  # type: ignore

        if cookies:
            response = query_instagram(latitude, longitude, cookies)
            if response:
                if response.status_code == HttpStatus.bad_request_400:
                    st.text("Cookies invalid. Please check again")

                if response.status_code == HttpStatus.too_many_requests_429:
                    st.text("Too many requests for 1 hour. Try again later")

                if response.status_code == HttpStatus.ok_200:
                    locations_df = pd.DataFrame(response.message.venues)
                    st.write(locations_df)
                    plot_coords(locations_df)
