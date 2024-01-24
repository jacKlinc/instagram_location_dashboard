import streamlit as st
import pandas as pd

from ..utils import plot_coords
from ..types import Page


class FileUpload(Page):
    def write(self):
        st.title("File Upload")
        # TODO: exception handling
        csv_file = st.file_uploader("Please choose a CSV file to upload...", type={"csv", "txt"})  # type: ignore
        if csv_file:
            gps_coords = pd.read_csv(csv_file)  # type: ignore
            plot_coords(gps_coords)
