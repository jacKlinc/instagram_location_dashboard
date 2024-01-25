import os
from dotenv import load_dotenv

from ..src.utils import InstagramVenue, query_instagram, calcualte_fuzzy_coordinates

load_dotenv(override=True)

lat, lng = 53.3, 6.2
venues_example = [
    {
        "external_id": 108146619209136,
        "external_id_source": "facebook_places",
        "name": "Kollumerpomp",
        "address": "0.5mi",
        "lat": 53.30451,
        "lng": 6.18946,
    },
    {
        "external_id": 116713638339323,
        "external_id_source": "facebook_places",
        "name": "Kollumerland",
        "address": "6mi",
        "lat": 53.2667,
        "lng": 6.06667,
    },
    {
        "external_id": 112697452074590,
        "external_id_source": "facebook_places",
        "name": "Warfstermolen",
        "address": "1.5mi",
        "lat": 53.29576,
        "lng": 6.2356,
    },
]

venues_example_expected = [
    (53.26767771872737, 6.057414932058087),
    (53.26767771872737, 6.128707466029043),
    (53.26767771872737, 6.2),
    (53.26767771872737, 6.271292533970957),
    (53.26767771872737, 6.342585067941913),
    (53.283838859363684, 6.057414932058087),
    (53.283838859363684, 6.128707466029043),
    (53.283838859363684, 6.2),
    (53.283838859363684, 6.271292533970957),
    (53.283838859363684, 6.342585067941913),
    (53.3, 6.057414932058087),
    (53.3, 6.128707466029043),
    (53.3, 6.271292533970957),
    (53.3, 6.342585067941913),
    (53.31616114063631, 6.057414932058087),
    (53.31616114063631, 6.128707466029043),
    (53.31616114063631, 6.2),
    (53.31616114063631, 6.271292533970957),
    (53.31616114063631, 6.342585067941913),
    (53.332322281272624, 6.057414932058087),
    (53.332322281272624, 6.128707466029043),
    (53.332322281272624, 6.2),
    (53.332322281272624, 6.271292533970957),
    (53.332322281272624, 6.342585067941913),
]


def test_query_instagram():
    """Tests if cookies work"""
    response_good = query_instagram(0, 0, os.getenv("INSTAGRAM_COOKIES"))
    assert response_good.status_code.value == 200


def test_calcualte_fuzzy_locations():
    locs = [InstagramVenue(**v) for v in venues_example]
    result = calcualte_fuzzy_coordinates(locs, lat, lng)
    expected = venues_example_expected

    assert result == expected
