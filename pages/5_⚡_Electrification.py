from PIL import Image
import streamlit as st
import requests
import numpy as np
import pandas as pd
from streamlit_lottie import st_lottie
import pydeck as pdk
from streamlit_extras.switch_page_button import switch_page
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show
from bokeh.transform import dodge, factor_cmap, factor_mark
from bokeh.models.callbacks import CustomJS
from bokeh.layouts import layout, column
from bokeh.models import HoverTool, LinearInterpolator
from bokeh.tile_providers import CARTODBPOSITRON, OSM, STAMEN_TONER, STAMEN_TERRAIN, get_provider
from bokeh.models.widgets import DateSlider
import math
from pyproj import Proj, transform
from pyproj import Transformer
from bokeh.palettes import GnBu3, OrRd3, Plasma, Category20

import os
path = os.path.dirname(__file__)
relative_path = '/data/'
path = os.path.dirname(__file__) #/var/www/html/etrak_site/pages
path_parent = os.path.dirname(path)
full_path = path_parent+relative_path
print('path: ', path, '. path_parent: ', path_parent)
s = 'path:  /var/www/html/cleanair/pages . path_parent:  /var/www/html/cleanair'
tooltip_css = '''
.tooltip {
  display: inline;
  position: relative;
  color=blue
}
.tooltip:hover:after {
    left: 50%;
    transform: translateX(-50%);
    background: white;
    color: black
}

.tooltip:hover:before {
    left: 50%;
    transform: translateX(-50%);
    background: white;
    color: black
} '''

# https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title='Clean Air Alliance Electrification', page_icon='📈', layout='wide')

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
electrification_coding = load_lottieurl('https://assets6.lottiefiles.com/packages/lf20_hbr24n88.json')

# --- WHAT I DO ---
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('## Electrification: the greatest industrial and societal development in the Modern Age')
    with col2:
        st_lottie(electrification_coding, width=100)
    col1, col2 = st.columns(2, gap='large')
    with col1:
        st.markdown('### Electrification for the climate and environment')
        electrification_blurb = 'Replacing fossil energy with electric energy at the consumer end will significantly expand the electric grid. But there&#8217;s a catch. The **environmental** benefits of electrification depend totally on the generation that makes the electricity. If that generation is based on combustible fuel, then the environmental benefits of electrification, in terms of air emissions, are only slightly better. Generation must be &#8220;smoke free&#8221;&mdash;i.e., non-emitting.'
        st.markdown(electrification_blurb)
        st.markdown('### Electrification only ensures that energy is &#8220;smoke free&#8221; at the user end')
        st.markdown('Smoke-free **generation** is absolutely essential to ensuring electrification results in clean energy all through the energy supply chain.')
        clean_list= """
        There are only two technologies that generate electricity in bulk, without any air pollution or greenhouse gases:
        1. Hydro.
        2. Nuclear.
        """
        st.markdown(clean_list)

    with col2: 
        st.markdown('### Sorry, but hydro&rsquo;s already taken')
        clean_list= """
        Most available hydroelectric resources in Ontario have been exploited since the dawn of the electrification era. This leaves nuclear, and variable renewables like wind and solar. However, wind and solar are not ***bulk*** electricity suppliers. And their variability is highly problematic.
        """
        st.markdown(clean_list)
        go_to_munis = st.button('See the Ontario Electricity page')
        if go_to_munis:
            switch_page('\U000e0063\U000e0061\U000e006f\U000e006e\U000e007f ontario electricity')
        #st.markdown('[See the Ontario Electricity page](/Ontario_electricity)')

        st.markdown('### Clean quiet power: a project list')
        ccp = '''
The &#8220;low hanging fruit&#8221; of electrification is the projects we can do right now, with available technology. These include
* Urban electrification.
* Grid expansion via rail.
* Power restoration: a new era.
* Construction site power.
* Mobile storage, not just cars.
* Small to medium scale (<100 kW) mobile storage applications.
        '''
        st.markdown(ccp)
        go_to_munis = st.button('Go to Municipalities page')
        if go_to_munis:
            switch_page('Municipalities')

    with col1: 


        st.markdown('### Options for grid-scale energy storage')
        storage_options = """
        The last available pumped storage site in Ontario, TC Energy&#8217;s facility at Meaford, is currently under development. That narrows the list of viable grid-scale energy storage options to thermal media&mdash;building mass and hot water. Chemical batteries have a role, but in small to medium-scale (less than 100 kW) applications, including cars and some heavier vehicles like buses and trucks.
        """
        st.markdown(storage_options)
        #--- beginning of proper ontario heat map
# --- ONTARIO "HEAT" MAP -- 
        df = pd.read_json('http://canadianenergyissues.com/data/on_weather_stationdata_noLDC.json').set_index('community_name')
        df['datehour_my'] = pd.to_datetime(df.datehour_my, unit='ms')
        df['community_name'] = df.index


        df= df.astype({'bearing':float, 'dewpoint':float, 'pressure':float, 'humidity':float, 'windspeed':float, 'temp':float, 'visibility':float, 'windchill':float, 'gust':float, 'realTemp':float, 'temp_delta':float, 'dwellings':float, 'ceiling_w':float, 'window_w':float, 'noWindowWall_w':float, 'floor_w':float, 'total_w':float, 'total_w_per_dwelling':float })

        #df = df.drop(['community_name.1', 'datehour_ec', 'datehour_my'], axis=1)
        df['Longitude'] = np.where(df.community_name=='Thunder Bay', -89.2477, df.Longitude)
        df['Longitude'] = np.where(df.community_name=='Kenora', -94.4894, df.Longitude)
        df['Latitude'] = np.where(df.community_name=='Thunder Bay', 48.382221, df.Latitude)
        df['Latitude'] = np.where(df.community_name=='Kenora', 49.766666, df.Latitude)

        z = [list(t) for t in zip(df.Longitude.values, df.Latitude.values)]
        df['COORDINATES'] = z
        df['total_w'] = df['total_w'].divide(1e6)

        df = df.copy()[['COORDINATES', 'datehour_my', 'total_w', 'community_name']]

               
        df['formatted_w'] = df['total_w'].apply(lambda d: '{0:,.0f}'.format(d) if d >= 1 else '{0:,.2f}'.format(d))
        dt = df['datehour_my'].values[0]
        dt = pd.to_datetime(dt).strftime('%a %b %d %I%p')
        df_sums = df['total_w'].sum()
        df_sums_dict = {'Bruce Nuclear Station Capacity':6000, 'Total Ontario Residential Heat Demand':df_sums,
            'Adam Beck 2 Hydro Generator':1630, 'TC Energy Pumped Storage Hydro':1000, 'Oneida Battery':250}
        df_totals = pd.DataFrame.from_dict(df_sums_dict, orient='index')
        df['datehour_formatted'] = pd.to_datetime(df['datehour_my']).dt.strftime('%a %b %d, %I%p')

        df_totals = pd.Series(df_sums_dict)

        layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        pickable=True,
        extruded=True,
        wireframe=True,
        get_elevation='total_w',
        radius=1.2e4,
        #get_fill_color=["total_w * 25", "total_w", "total_w * 25", 220],
        get_fill_color=[50, 0, 0, 50],
        elevation_scale=500,
        get_position="COORDINATES",
        auto_highlight=True
        )

        lat = 46.3862 # Elliott Lake ON
        lon = -82.6509
        lat = 43.4516 # kitchener on
        lon = -80.4925

       
        view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=4.75, bearing=0, pitch=50, height=350 )
        tooltip = {
        "html": "<b>{community_name}:<br> {formatted_w}</b> MW heat demand</b>",
        "style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial', "z-index": "10000"},
        }
        tooltip = {
                    "html": "<style> "+tooltip_css+" </style> <div class='tooldip'><b>{community_name}, {datehour_formatted}:<br> {formatted_w} MW</b> residential space heat demand </b></div>",
            "style": {"background": "lightgrey", "color": "black", "font-family": '"Helvetica Neue", Arial', "z-index": "10000", "display": "inline",
    "position":"relative",
    "display":"block",
    "top": "-25%",
    "left": "5%",
    "width":"50%",
    "margin-left":"-25%",
    "text-align": "left"},
            }

        # Render
        r = pdk.Deck(
        layers=[layer],
        map_style='road',
        initial_view_state=view_state,
        tooltip=tooltip,
        )

        st.pydeck_chart(r)
    st.markdown('### Squaring circles: Canada&#8217;s electrification challenge')
    st.markdown('''
    &#8220;Net Zero By 2050&#8221; requires generating most if not all electricity with non-emitting technologies. There are currently roughly 1,100 power generating facilities across Canada. Over 900 of them&mdash;80 percent&mdash;are non-emitting. 

    The map below shows most of Canada&#8217;s power plants. Circle shapes represent combustible-fueled (emitting) generation capacity, squares represent non-emitting. &#8220;Net Zero By 2050&#8221; means squaring most of those circles.

    Most combustible-fueled generation is in Alberta, Saskatchewan, Ontario, New Brunswick, and Nova Scotia. The vast bulk of generation, and emissions, occur in Alberta, which has a combustible baseload supply of 7,000 to 9,000 MW depending on the season.

    Decarbonizing the latter with non-emitting generation is possible only with nuclear. This would entail nuclearizing oilsands process heat, since most of Alberta's baseload supply comes from oilsands operations where electric power is &#8220;cogenerated&#8221; with process heat. Replacing the gas that currently provides process heat would free up natural gas for export into the new global LNG market. This could represent a major new market for the Alberta oil and gas sector.
    

    ''')
#--begin canada map --
    data = pd.read_csv(full_path+'can_usa_powerplants_lon_lat.csv')
    canada_mask = data.country_long=='Canada'
    data = data[canada_mask]
    
    color_map = {'Nuclear':'blue', 'Coal':'black', 'Gas':'purple', 'Wave and Tidal':'green', 'Oil':'gray', 'Other': 'lightgray', 'Biomass':'brown', 'Hydro':'skyblue', 'Wind':'yellow', 'Solar':'orange'}
    other_types = ['Cogeneration' 'Storage' 'Geothermal' 'Petcoke']
    cvn_map = {'Nuclear':'Non-combustible', 'Coal':'Combustible', 'Gas':'Combustible', 'Wave and Tidal':'Non-combustible', 'Oil':'Combustible', 'Other': 'Combustible', 'Biomass':'Combustible', 'Hydro':'Non-combustible', 'Wind':'Non-combustible', 'Solar':'Non-combustible', 'Waste': 'Combustible', 'Cogeneration':'Combustible', 'Storage':'Non-combustible', 'Geothermal':'Non-combustible', 'Petcoke':'Combustible'}
    data['color'] = data.primary_fuel.map(color_map)
    data['cvn'] = data.primary_fuel.map(cvn_map)
    def getLineCoords(row, geom, coord_type):
        """Returns a list of coordinates ('x' or 'y') of a LineString geometry"""
        if coord_type == 'x':
            return list( row[geom].coords.xy[0] )
        elif coord_type == 'y':
            return list( row[geom].coords.xy[1] )
    
    MARKERS = [ 'circle', 'square']
    CVN = ['Combustible', 'Non-combustible']
    tile_provider = get_provider(OSM)
    figtitle = '''
Canada installed power generation capacity:\nCombustible (square) and Non-combustible (circle)
    '''
    p_canadaMap = figure(title=figtitle, x_axis_type="mercator", y_axis_type="mercator")
    
    p_canadaMap.yaxis.axis_label = 'Latitude'
    p_canadaMap.xaxis.axis_label = 'Longitude'
    
    data = data.drop('geometry', axis=1).copy()
    dsource = ColumnDataSource(data)
    nc_mask = data['cvn']=='Non-combustible'
    c = data[~nc_mask]
    c_mask = c['cvn']=='Combustible'
    index_cmap = factor_cmap('primary_fuel', palette=Category20[15], factors=sorted(data.primary_fuel.unique()))
    mw_mapper = LinearInterpolator(x=[data.capacity_mw.min(), data.capacity_mw.max()], y=[5,100])
    p_canadaMap.scatter(x='x', y='y', source=dsource, line_color='black', color=index_cmap, size={'field':'capacity_mw', 'transform':mw_mapper}, marker=factor_mark('cvn', MARKERS, CVN), legend_field='primary_fuel')
    
    p_canadaMap.add_tile(tile_provider)
    my_hover = HoverTool()
    my_hover.tooltips = [('Name of plant', '@name'),('Province', '@name'),  ('Capacity MW', '@capacity_mw'), ('Fuel', '@primary_fuel')]
    p_canadaMap.add_tools(my_hover)
    p_canadaMap.sizing_mode='stretch_both'
    p_canadaMap.legend.label_text_font_size='14pt'
    p_canadaMap.legend.glyph_height=50
    p_canadaMap.legend.glyph_width=50
    st.bokeh_chart(p_canadaMap)

    #-- end canada map --
    st.markdown('### Major areas of electrification opportunity')
    st.markdown('''
    CNWC publishes a [series of policy position papers](https://cnwc-cctn.ca/category/policy-positions/) that identify major areas of activity and suggest ways to achieve electrification as expeditiously as possible.
    
    These areas are:
    
    1. Road and rail transport.
    * Direct from grid.
    * Battery-based.
    1. Industrial.
    * Data Centres.
    * Vertical farms.
    * Hot water.
    * Heat pumps.
    1. Urban on- and &#8220;off-grid&#8221; applications.
    * Construction site power.
    * Mobile non-EV batteries, e.g. film sets.
    * Recreational site power, e.g. public parks and recreation areas.
    ''')
    #--- end of proper ontario heat map

    with col2:
        st.markdown('### The role of rail in higher electricity availability standards')
        storage_options = """
        The May 21 2022 derecho in eastern Ontario and west Quebec highlighted the impact of &#8220;black swan&#8221; events on critical electricity infrastructure. Areas of Ottawa, a G-7 capital, were without power for weeks. Luckily, the weather following the storm was relatively benign, with outdoor temperatures not exceeding 28°C during those weeks.

        Under electrification, such outages must not occur. With geographically far-flung electricity systems like those across Canada, it will be a challenge to reach and maintain heightened availability standards.

        The national rail system has a critical role to play in this. Often rail lines are spatially proximate to electricity transmission. This gives railroads physical access to the system, which opens the possibility of transporting heavy transformers and even substations that could help restore power to blacked-out areas.

        This in turn opens a new business to railroads, much of whose business today consists of transporting hydrocarbons.
        """
        st.markdown(storage_options)

