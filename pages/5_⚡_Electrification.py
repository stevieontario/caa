from PIL import Image
import streamlit as st
import requests
import numpy as np
import pandas as pd
from streamlit_lottie import st_lottie
import pydeck as pdk
from streamlit_extras.switch_page_button import switch_page

import os
path = os.path.dirname(__file__)
relative_path = '/data/'
path = os.path.dirname(__file__) #/var/www/html/etrak_site/pages
path_parent = os.path.dirname(path)
full_path = path_parent+relative_path


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

        # --- ONTARIO "HEAT" MAP -- 
        df = pd.read_csv(full_path+'ontario_heat_demand.csv', header=0)
        print(df.head())
        df['Longitude'] = np.where(df.community_name=='Thunder Bay', -89.2477, df.Longitude)
        df['Longitude'] = np.where(df.community_name=='Kenora', -94.4894, df.Longitude)
        df['Latitude'] = np.where(df.community_name=='Thunder Bay', 48.382221, df.Latitude)
        df['Latitude'] = np.where(df.community_name=='Kenora', 49.766666, df.Latitude)

        z = [list(t) for t in zip(df.Longitude.values, df.Latitude.values)]
        df['COORDINATES'] = z
        df['total_w'] = df['total_w'].divide(1e6)
        df = df.copy()[['COORDINATES', 'total_w', 'community_name']]
               
        df['formatted_w'] = df['total_w'].apply(lambda d: '{0:,.0f}'.format(d) if d >= 1 else '{0:,.2f}'.format(d))
        layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        pickable=True,
        extruded=True,
        get_elevation='total_w',
        radius=5e3,
        get_fill_color=["total_w * 25", "total_w", "total_w * 25", 220],
        elevation_scale=500,
        get_position="COORDINATES",
        auto_highlight=True
        )

        lat = 46.3862 # Elliott Lake ON
        lon = -82.6509
       
        view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=4.255, bearing=0, pitch=45)
        tooltip = {
        "html": "<b>{community_name}:<br> {formatted_w}</b> MW heat demand</b>",
        "style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial', "z-index": "10000"},
        }
        # Render
        r = pdk.Deck(
        layers=[layer],
        map_style='road',
        initial_view_state=view_state,
        tooltip=tooltip,
        )
        r.to_html("grid_layer.html")

        st.markdown('##### Ontario residential space heating demand')
        space_heating = '''
On cold days, the demand for space heating in Ontario communities outstrips that for electricity.
        '''
        st.markdown(space_heating)
        st.pydeck_chart(r)

    with col2:
        st.markdown('### The role of rail in higher electricity availability standards')
        storage_options = """
        The May 21 2022 derecho in eastern Ontario and west Quebec highlighted the impact of &#8220;black swan&#8221; events on critical electricity infrastructure. Areas of Ottawa, a G-7 capital, were without power for weeks. Luckily, the weather following the storm was relatively benign, with outdoor temperatures not exceeding 28°C during those weeks.

        Under electrification, such outages must not occur. With geographically far-flung electricity systems like those across Canada, it will be a challenge to reach and maintain heightened availability standards.

        The national rail system has a critical role to play in this. Often rail lines are spatially proximate to electricity transmission. This gives railroads physical access to the system, which opens the possibility of transporting heavy transformers and even substations that could help restore power to blacked-out areas.

        This in turn opens a new business to railroads, much of whose business today consists of transporting hydrocarbons.
        """
        st.markdown(storage_options)

