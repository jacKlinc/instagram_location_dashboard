import streamlit as st


def mapping_demo():
    import pandas as pd

    @st.cache_data  # type: ignore
    def from_data_file(filename):
        return pd.read_csv(filename)

    try:
        df = from_data_file("./data/locs.csv")
        lat_lng = df[["lat", "lng"]].dropna()
        # st.table(lat_lng)
        st.map(lat_lng, longitude='lng',) # type: ignore
    except FileNotFoundError as e:
        st.error(e)


mapping_demo()
