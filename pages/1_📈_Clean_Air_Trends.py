from PIL import Image
import streamlit as st
import requests
import numpy as np
import pandas as pd
from streamlit_lottie import st_lottie
import geopandas as gpd
pd.set_option('plotting.backend', 'pandas_bokeh')

import html
from bs4 import BeautifulSoup
import urllib
import urllib.request
import re
from bokeh.sampledata.autompg import autompg_clean as dfb
from bokeh.models import ColumnDataSource
from bokeh.palettes import GnBu3, OrRd3
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, Grid, HBar, LinearAxis, Plot, Div
import bokeh as bk


import os
path = os.path.dirname(__file__)
relative_path = '/data/'
path = os.path.dirname(__file__) #/var/www/html/etrak_site/pages
path_parent = os.path.dirname(path)
full_path = path_parent+relative_path

tableau_colors = ["#4e79a7","#f28e2c","#e15759","#76b7b2","#59a14f","#edc949","#af7aa1","#ff9da7","#9c755f","#bab0ab"]

tools=["pan,wheel_zoom,box_zoom,reset,save, ybox_zoom"]
# https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title='Clean Air Alliance Data', page_icon='📈', layout='wide')

# --- LOAD ASSETS ---
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


heater_coding = load_lottieurl('https://assets8.lottiefiles.com/packages/lf20_FCYi2l.json')
temp_coding = load_lottieurl('https://assets8.lottiefiles.com/packages/lf20_m4znnezt.json')
hotPerson_coding = load_lottieurl('https://assets8.lottiefiles.com/packages/lf20_medwe7cs.json')
airPollution_coding = load_lottieurl('https://assets5.lottiefiles.com/packages/lf20_OFvr8Nvcmq.json')
st_lottie(airPollution_coding, width=400)

st.markdown('## Fighting climate change is the same as fighting air pollution')
st.markdown('Power plants that produce air pollution also produce greenhouse gases. To eliminate both air pollution and GHGs, power plants must be zero emitting. Only hydro and nuclear are truly zero emitting.')


## Show in webpage
st.markdown('## Ontario&#8217;s Clean Air energy system')
st.markdown('In an all-electric future, Ontario&#8217;s electric grid will be even more vital than it is today. How will it expand from its current locations, which are shown in the map below? Chances are it will appear similar zoomed out, but zoomed in there will be significant expansion, especially in and around urban areas.')
st.markdown('Note that at all of the end-user points of this system, ***all energy comes with zero emissions***. If electricity provided all energy, it would eliminate most combustion-produced air pollutants, including most of those measured at the stations shown on the map.')
#st.components.v1.html(html_data,height=500)

# --- ONTARIO AQ STATIONS DATA --
on_stations = pd.read_csv(full_path+'on_aq_stations.csv').set_index('Station Information')
on_stations.index = pd.Index([el[:-1] for el in on_stations.index])
on_stations.columns = on_stations.iloc[0].values
on_stations = on_stations.T
convert_dict = {'Latitude':float, 'Longitude':float}
on_stations = on_stations.astype(convert_dict)
on_stations['Station'] = on_stations.index 
cols = ['Station Name', 'Address', 'y', 'x', 'Station Type',
       'Height of Air Intake', 'Elevation ASL', 'Pollutants Measured',
       'Station']
on_stations['info'] = 'Station: '+on_stations['Station Name']+'.\n Address: '+on_stations['Address']+'.\n Pollutants measured: '+on_stations['Pollutants Measured']+'.\n Height of Air Intake: '+on_stations['Height of Air Intake']+'.'
on_stations['info'] = on_stations['info'].str.replace('..', '.', regex=False)

print(on_stations.columns)
on_stations_lonlat = gpd.GeoDataFrame(on_stations[['Longitude', 'Latitude']], geometry=gpd.points_from_xy(on_stations['Longitude'], on_stations['Latitude']))
station_source = ColumnDataSource(on_stations_lonlat)
# ---

ut =  gpd.read_file('/home/steveaplin/Downloads/Utility_Line/Utility_Line.shp')
ut_orig = ut.copy()
pb = ut_orig.plot_bokeh(line_width=2, color='green', title='Ontario transmission network', tile_provider='OSM', show_figure=False)
#pb.circle('x', 'y',  source=station_source, color='red', size=20)


# --- DIRTY AIR ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.bokeh_chart(pb)
        st.markdown('## Cars, trucks, trains, stoves, furnaces: the sources of dirty air')
        cleanAirData_blurb = '''
        Motor vehicle road transportation and heating are Canada&#8217;s largest sources of greenhouse gases and air pollution, by far. And cities&mdash;especially urban canyons between large buildings&mdasn;are where dangerous pollutants are found in their highest concentrations. These include
        * Ground-level ozone (O₃).
        * Particulate matter (PM).
        * Oxides of nitrogen (NOx).
        * Oxides of sulphur (SOx).
        * Carbon monoxide (CO).
        These are mainly the products of combustion of hydrocarbon fuels, mostly gasoline, diesel, and natural gas.
        '''
        st.markdown(cleanAirData_blurb)
        st.markdown('## Electrification fights indoor air pollution too')
        indoor_air_blurb = '''
A major and downplayed factor affecting human health is indoor air pollution. This is particularly a concern in households with gas stoves and furnaces requiring pilot lights, which can cause dangerous buildups of carbon monoxide (CO). CO is the most prolific toxic killer in human history. Pilot lights require several fail-safe measures to prevent CO buildup, and these fail-safes must be continuously monitored and tested.

Electrification eliminates the need for pilot lights, because it removes the need for combustible-fuels entering your home in the first place.
        '''
        st.markdown(indoor_air_blurb)
        st.markdown('## Minor sources of dirty air: major sources of noise')
        cleanAirData_blurb = '''
        Combustion engines not only pollute their air, but because of the sheer noise they produce they also seriously detract from urban quality of life. Applications include
        * Portable/towable generators.
        * Gardening equipment like mowers, trimmers, chainsaws, blowers.
        '''
        st.markdown(cleanAirData_blurb)
    with col2:

        cols = ['O₃ (ppb)', 'PM₂.₅ (µg/m³)', 'NO₂ (ppb)', 'SO₂ (ppb)', 'CO (ppm)']
        pollutant = st.radio(label='Choose pollutant', options=cols, horizontal=True, label_visibility='visible')
        url = 'http://www.airqualityontario.com/history/summary.php'
        result = urllib.request.urlopen(url)
        soup = BeautifulSoup(result, 'lxml')
        soup = html.unescape(soup)

        h1 = soup.findAll('h1')[1].text
        tbody = soup.findAll('tbody')
        td = soup.findAll('td')
        lar = []
        for t in td:
            lar.append(t.text)
        lar = [s.strip() for s in lar]
        locations = lar[::6]
        o3 = np.array(lar[1:][::6])
        pm2 = np.array(lar[2:][::6])
        no2 = np.array(lar[3:][::6])
        so2 = np.array(lar[4:][::6])
        co = np.array(lar[5:][::6])
        df = pd.DataFrame(np.column_stack((o3, pm2, no2, so2, co)), index=locations, columns=cols)
        df.replace('N/A', np.NaN, inplace=True)
        df.replace('', np.NaN, inplace=True)
        df = df.astype(float)
        df = df.sort_index(ascending=False)
        x = df[pollutant]
        y = df.index
        p = figure(
        title= 'Outdoor '+h1,
        y_range=y.values,
        x_axis_label=pollutant,
        y_axis_label='')
        color = tableau_colors[cols.index(pollutant)]
        p.hbar(right=x, y=y, height=0.5, color=color)
        st.bokeh_chart(p)
        with st.expander('See the data for the above chart'):
            aq_expander_blurb = '''
**Source**: [Ontario Ministry of the Environment, Conservation, and Parks](http://www.airqualityontario.com/history/summary.php)
            '''
            aq_expander_blurb = h1+'\n'+aq_expander_blurb
            st.markdown(aq_expander_blurb)
            st.dataframe(df.sort_index(ascending=True))
        
        st.markdown('## Electrification: the all-important generation side')
        cleanAirData_blurb = '''
        Electricity can be smokeless at both ends: generation **and** end use. Generation is critical. There are only a very narrow range of options for ensuring smoke-free electricity generation:
        * Hydro.
        * Variable renewable energy (VRE).
        * Nuclear.
        Because VRE depends on dispatchable power sources, a VRE-intensive system must include either hydro or nuclear or both. Most electricity systems in Canada have already tapped their available hydro resources. This leaves only nuclear as the backbone of expanded electricity generation.
        '''
        st.markdown(cleanAirData_blurb)
        l = '[See Muncipalities page](/Municipalities)'
        st.markdown(l)
        on_stations = pd.read_csv(full_path+'on_aq_stations.csv').set_index('Station Information')
        on_stations.index = pd.Index([el[:-1] for el in on_stations.index])
        on_stations.columns = on_stations.iloc[0].values
        on_stations_latlon = on_stations.loc['Latitude':'Longitude'].T
        on_stations_latlon.columns = ['lat', 'lon'] 
        on_stations_latlon = on_stations_latlon.astype(float)
        #st.map(on_stations_latlon)
    with col1:
        st.markdown('## What we ***don&#8217;t*** know about urban outdoor air pollution')
        what_we_know = '''
The map above shows the locations of the Ontario provincial ministry&#8217;s air quality monitoring stations in Ontario. As you can see, there are relatively few stations. Toronto, Canada&#8217;s largest city, has only four. Of these, only one (Toronto West) measures carbon monoxide, the most prolific toxic killer in the world. This in spite of the fact that there are literally tens of thousands of CO-emitting motor vehicles passing literally within meters of tens of thousands of pedestrians during most hours of every day.
        '''
        st.markdown(what_we_know)



