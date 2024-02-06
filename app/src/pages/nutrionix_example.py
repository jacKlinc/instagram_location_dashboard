import asyncio
import time
import os
from dotenv import load_dotenv

import httpx
import streamlit as st


load_dotenv(override=True)

HEADERS = {"Cookie": os.getenv("INSTAGRAM_COOKIES"), "Content-Type": "application/json"}
INSTAGRAM_URL = "https://www.instagram.com/location_search/"

insta_result = []


async def get_insta(client: httpx.AsyncClient, lat: float, lng: float):
    params = {"latitude": lat, "longitude": lng}
    r = await client.get(INSTAGRAM_URL, params=params, headers=HEADERS)

    venue = {"coord": f"{str(lat)}, {str(lng)}", "venues": r.json()["venues"]}
    insta_result.append(venue)


async def main():
    async with httpx.AsyncClient(headers=HEADERS) as client:
        fuzzy_locations = [
            (52.9, 5.8),
            (52.9, 5.9),
            (52.9, 6),
            (52.9, 6.1),
            (52.9, 6.2),
        ]

        tasks = [
            asyncio.create_task(get_insta(client, k[0], k[1])) for k in fuzzy_locations
        ]
        await asyncio.gather(*tasks)


start_time = time.time()
asyncio.run(main())

st.write(insta_result)
