import streamlit as st
from streamlit_js_eval import get_geolocation
import pandas as pd
import numpy as np
import math
from math import radians, cos, sin, asin, sqrt
from vincenty import vincenty

size = 20
start = [52.52052, 13.29726, "Start", "#dc143c", size]
gardener = [52.52181, 13.29594, "Gardener", "#dc143c", size]
skippingStones = [52.52275, 13.29699, "Girl Skipping Stones", "#dc143c", size]
kid = [52.52517, 13.29334, "Kid", "#dc143c", size]
father = [52.52245, 13.29518, "Father in Law", "#dc143c", size]
mother = [52.5231, 13.29318, "Sophia Charlotte of Hanover", "#dc143c", size]
duck = [52.52374, 13.29522, "Duck Pond", "#dc143c", size]
philosopher = [52.524, 13.29183, "Philosopher", "#dc143c", size]
minerva_statue = [52.52161, 13.29343, "Minerva Statue", "#dc143c", size]
nanny = [52.52438, 13.29341, "Nanny", "#dc143c", size]
guard = [52.52105, 13.29093, "Guard", "#dc143c", size]
lady = [52.52497, 13.29027, "Lady", "#dc143c", size]
fisher = [52.52643, 13.29486, "Fisher", "#dc143c", size]

allPts = [start,gardener,skippingStones,kid,father,mother,duck,philosopher,minerva_statue, nanny, guard, fisher, lady]

#temporary user lat and lng coords
#lat = 52.520008
#lng = 13.404954

#consts for vincenty???
a = 6378137  # meters
f = 1 / 298.257223563
b = 6356752.314245
MILES_PER_KILOMETER = 0.621371
MAX_ITERATIONS = 200
CONVERGENCE_THRESHOLD = 1e-12

def allBounds(lat, lng):
    out = []
    for loc in allPts:
        #if user within radius 50m (approx)
        if(vincenty_dist(lat, lng, loc[0],loc[1])<=.05):
            print(vincenty_dist(lat, lng, loc[0],loc[1]))
            print(out)
            out.append(loc)

    return out

def vincenty_dist(lat, lng, lat1,lng1):
    return vincenty((lat,lng),(lat1,lng1), miles=False)

df = pd.DataFrame(
    allPts,
    columns=['lat', 'lon', "name", "color", "size"])

loc = get_geolocation()

if loc != None:
    loc = loc["coords"]
    lat = loc["latitude"]
    lng = loc["longitude"]

    new_row = {'lat':float(lat), 'lon':float(lng), "name": "USER", "color": "#02a9f7", "size" : size}
    df = df.append(pd.Series(new_row, index=df.columns, name='7'))
    pts = allBounds(lat, lng)

    st.write("## You can interact with :")
    st.write("<b>"+ "<br>".join([i[2] for i in pts]) + "</b>", unsafe_allow_html = True)

st.map(df, color="color", size = "size")
