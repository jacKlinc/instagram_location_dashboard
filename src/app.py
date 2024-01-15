import streamlit as st
import pandas as pd


# Sections
def mapping_demo():
    @st.cache_data  # type: ignore
    def from_data_file(filename):
        return pd.read_csv(filename)

    try:
        df = from_data_file("./data/locs.csv")
        plot_coords(df)
    except FileNotFoundError as e:
        st.error(e)


def instagram_search():
    st.header("Instagram Search")
    st.text(
        "This section will use the existing Bellingcat repo to search for activity in an area"
    )

    # TODO: add regex to for check correct format
    cookies = st.text_input("Please enter your Instagram cookies", type="password")

    # TODO: add regex to for check correct format
    latitude_north = st.text_input("Please enter the northerly latitude")
    latitude_south = st.text_input("Please enter the southerly latitude")
    longitude_west = st.text_input("Please enter the westerly longitude")
    longitude_east = st.text_input("Please enter the easterly longitude")
    
    st.text("This does nothing for now")


def file_upload():
    st.header("Upload File")
    # TODO: exception handling
    csv_file = st.file_uploader("Please choose a CSV file to upload...", type={"csv", "txt"})  # type: ignore
    if csv_file:
        gps_coords = pd.read_csv(csv_file)
        plot_coords(gps_coords)


# Utils
def plot_coords(df: pd.DataFrame):
    """Plots GPS coordinates on Streamlit map

    Args:
        df (pd.DataFrame): table of latitudes and longitudes
    Only works where columns named: "lat", "lng"
    """
    # TODO: exception handling
    lat_lng = df[["lat", "lng"]].dropna()
    st.map(lat_lng, longitude="lng")  # type: ignore


# Main
data_sources = ["Instagram Search", "Upload your own file"]
data_choice = st.radio("Choose where the data comes from", data_sources)

if data_choice == data_sources[0]:
    instagram_search()


if data_choice == data_sources[1]:
    file_upload()


st.header("Example")
st.markdown(
    "Fromt the Tucson, Arizona example in the [instagram-location-search](https://github.com/bellingcat/instagram-location-search) repo"
)

if st.button("See example from GitHub"):
    mapping_demo()
