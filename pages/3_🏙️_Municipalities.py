from PIL import Image
import streamlit as st
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import html
import matplotlib.ticker as mtick
from matplotlib.dates import DateFormatter
from matplotlib.dates import HourLocator
from matplotlib.dates import DayLocator
import matplotlib.dates as mdates
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.palettes import GnBu3, OrRd3, Category10, Category20, Category20b, Category20c
colors = Category20[20]+Category20b[20]+Category20c[20]+Category10[10]
from bokeh.plotting import figure, show
from bokeh.models import DatetimeTickFormatter
from streamlit_lottie import st_lottie
from bokeh.models import Span
from bokeh.models import HoverTool
from bokeh.tile_providers import CARTODBPOSITRON, OSM, STAMEN_TONER, STAMEN_TERRAIN, get_provider
import geopandas as gpd

import xyzservices.providers as xyz
import os
path = os.path.dirname(__file__)
relative_path = '/data/'
path = os.path.dirname(__file__) #/var/www/html/etrak_site/pages
path_parent = os.path.dirname(path)
full_path = path_parent+relative_path


# https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title='Clean Air Alliance Municipalities', page_icon=':sunflower:', layout='wide')

def getLineCoords(row, geom, coord_type):

    """Returns a list of coordinates ('x' or 'y') of a LineString geometry. From https://automating-gis-processes.github.io/2016/Lesson5-interactive-map-bokeh.html"""
    if coord_type == 'x':
        return list( row[geom].coords.xy[0] )
    elif coord_type == 'y':
        return list( row[geom].coords.xy[1] )


# --- LOAD ASSETS ---
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lightbulb_coding = load_lottieurl('https://assets4.lottiefiles.com/private_files/lf30_psn7xxju.json')
tree_coding = load_lottieurl('https://assets4.lottiefiles.com/packages/lf20_BhbCTg.json')
battery_coding = load_lottieurl('https://assets4.lottiefiles.com/packages/lf20_DwG3RkOkYV.json')
heater_coding = load_lottieurl('https://assets8.lottiefiles.com/packages/lf20_FCYi2l.json')
revenue_coding = load_lottieurl('https://assets9.lottiefiles.com/private_files/lf30_wypj5bum.json')
tableau_colors = ["#4e79a7","#f28e2c","#e15759","#76b7b2","#59a14f","#edc949","#af7aa1","#ff9da7","#9c755f","#bab0ab"]
endash = u'\u2013'

tools=["pan,wheel_zoom,box_zoom,reset,save,hover,xbox_zoom, hover"]

# SELECTION BOX EXAMPLE
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('## Municipalities as energy providers&mdash;and money makers')
    with col2:
        st_lottie(revenue_coding, width=200)
    col1, col2 = st.columns(2, gap='large')
    with col1:
        st.markdown('### Electrification: a revolution for municipalities')
        munis_blurb = 'With electrification, municipal electric utilities will take over from gasoline and natural gas retailers as the predominant energy providers. The amount of energy they distribute will triple, perhaps quadruple. So will their revenues.'
        st.write(munis_blurb)
        st.image(full_path+'3_energies_4_dims.png')
        st.markdown('### Inflation-proof energy')
        st.markdown('Because electrification will necessitate a massive expansion of bulk electricity generation, economies of scale will drive the cost and price of electricity down, reversing the trend of escalating costs and prices that has developed over the past two decades.')
        st.markdown('### The geography of electrification')
        st.markdown('The LDCs on the map represent the geographic and corporate centres of electrical power in Ontario. These areas are of course also very significant ***energy*** centres, in that they contain many thousands of individual stationary and mobile combustion engines, in the form of car engines and home furnaces. With widespread electrification, these corporations will become the main ***energy*** providers in their communities, replacing filling stations and gas companies as the primary providers of transportation and heating energy.')
        # --- BOKEH ONTARIO LDC MAP --
        ldc = gpd.read_file(full_path+'ldc.shp')
        ldc['geometry'] = ldc['geometry'].to_crs(3857)
        ldc['geometry'] = ldc.geometry.boundary
        ldc['area'] = ldc.copy().area
        ldc = ldc.explode()
                
        ldc['x'] = ldc.apply(getLineCoords, geom='geometry', coord_type='x', axis=1)
        
        # Calculate y coordinates of the line
        ldc['y'] = ldc.apply(getLineCoords, geom='geometry', coord_type='y', axis=1)
        l = ldc.drop('geometry', axis=1).copy()[['Name', 'x', 'y']]
        ldcs = np.unique(l.Name)
        ldc = st.multiselect('Choose an LDC', ldcs, 'Toronto Hydro-Electric System Limited')
        l = l[l['Name'].isin(ldc)]
        ldcs = np.unique(l.Name)
        cs = zip(ldcs, colors)
        csd = {c[0]:c[1] for c in cs}
        l['color'] = l['Name'].map(csd)
        print('is l mapped right? ', l[['Name', 'color']])
        lsource = ColumnDataSource(l)
        p_ldc = figure(title='LDCs in Ontario', tools='box_select,tap,pan,wheel_zoom,reset, save, hover', x_axis_type="mercator", y_axis_type="mercator")
        p_ldc.multi_line('x', 'y', source=lsource, line_color='color', line_width=3)
        tile_provider = get_provider(STAMEN_TERRAIN)
        #tile_provider = get_provider(xyz.OpenStreetMap.Mapnik)
        p_ldc.add_tile(tile_provider)
        p_ldc.yaxis.axis_label = 'Latitude'
        p_ldc.xaxis.axis_label = 'Longitude'
        hover = p_ldc.select(dict(type=HoverTool))
        hover.tooltips = [("LDC name", "@Name")]
        hover.mode = 'mouse'

        st.bokeh_chart(p_ldc)

        # --

    with col2:
        st.markdown('### Variable renewable energy sources increase electricity system costs, reduce LDC revenue')
        st.markdown('VRE resources increase system costs, because they reduce the operating efficiency of the supply sources that play the biggest role in meeting net demand. When those &#8220;balancers&#8221; are themselves non-emitting, the VRE sources are superfluous to meeting climate goals, and in many cases detrimental. By increasing system costs and thereby prices, VRE sources make grid electricity less economically competitive next to cheap hydrocarbons. In Ontario, grid electricity is four to five times as expensive as natural gas, per unit of energy&mdash;and that is in spite of the carbon tax which is applied to natural gas but not electricity.')


        st.markdown('### Dramatic rise in urban air quality')
        st.markdown('The overwhelming cause of poor urban air quality is gasoline and diesel powered road vehicles')
        st.markdown('### Municipalities have a direct stake in electricity price reform')
        st.markdown('With stable clean affordable electric power, city and town governments will see unprecedented prosperity. However, this can only happen with true affordability. Economies of scale at the generation end of the power supply chain is the only proven way to achieve this.')
        st.markdown('### Employment implications of electrification: growing the proportion of high-skilled jobs')
        st.markdown('With stable clean affordable electric power, city and town governments will see unprecedented prosperity. However, this can only happen with true affordability. Economies of scale at the generation end of the power supply chain is the only proven way to achieve this.')
