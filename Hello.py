from PIL import Image
import streamlit as st
from annotated_text import annotated_text
from streamlit.components.v1 import html
import requests
from streamlit_lottie import st_lottie
from st_pages import Page, show_pages, add_page_title

import os
path = os.path.dirname(__file__)
relative_path = '/data/'
path = os.path.dirname(__file__) #/var/www/html/etrak_site/pages
path_parent = os.path.dirname(path)
full_path = path_parent+relative_path

def V_SPACE(lines):
    for _ in range(lines):
        st.write('&nbsp;')

# https://www.webfx.com/tools/emoji-cheat-sheet/

#var = '2_🏴󠁣󠁡󠁯󠁮󠁿_Ontario_electrici'
st.set_page_config(page_title='CleanAir home', page_icon=':sunflower:', layout='wide')
#show_pages(
    #[
        #Page("/var/www/html/cleanair/Hello.py", "Home", "🏠"),
        #Page("/var/www/html/cleanair/pages/1_📈_Clean_Air_Trends.py", "/var/www/html/cleanair/pages/"+var, "/var/www/html/cleanair/pages/3_🏙️_Municipalities.py", "pages/4_📊_Energy_Forecasting.py", "pages/5_⚡_Electrification.py"),
    #]
#)
# --- LOAD ASSETS ---
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

house_energy = load_lottieurl('https://assets4.lottiefiles.com/packages/lf20_ulfrygzw.json')
meeting_json = load_lottieurl('https://assets1.lottiefiles.com/packages/lf20_7mpsnbrj.json')
image_contact_form = Image.open(path+'/images/contact.png')

# --- USE LOCAL CSS ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
local_css(path+'/style/style.css')

#--- SET BACKGROUND IMAGE FOR THIS PAGE ---
import base64

@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    body {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str

    st.markdown(page_bg_img, unsafe_allow_html=True)
    return

#set_png_as_page_bg('/home/steveaplin/Documents/eda/caa_avatar.png')
#--- HEADER SECTION ---
with st.container():
    st.image(path+'/images/CA-Canada-Flag-icon.png', width=50)
    st.subheader('Energy & Environment')
    st.title('We are the Canadian Clean Air Alliance :wave:')
    st.markdown('## &#8220;Promoting clean air through clean electrical energy&#8221;')
    promoting_blurb = '''
    We advocate for proven, realistic ways to achieve clean air, through actual clear energy. The Canadian provinces of Ontario and Quebec are the two greatest examples in North America of the electrical transition that is coming. Both have uncommonly clean electricity. Quebec&mdash;with long, cold winters&mdash;heats mostly with electricity, one of the few jurisdictions in North America that does so. Given that heating represents by far the single biggest energy use category in all Canadian provinces, that&#8217;s quite an achievement.

    Ontario originally depended on hydropower, but as it grew it developed North America&#8217;s largest nuclear power generation fleet, based on technology invented in Canada by Canadians.

    Together, Quebec and Ontario show the way forward with electrification: 
    1. Heat electrically.
    2. All new generation capacity should be nuclear.
    '''
    st.markdown(promoting_blurb)
    why_caa = 'Clean air is within our reach, and we can achieve it with proven, available technology, without sacrificing comfort and quality of life. Canada&#8217;s environment and economy deserve strong, honest, fact-based representation in the energy sector. At the Canadian Clean Air Alliance, we engage the public and policymakers with good information on this critical subject, to cut through the distortions and misinformation that often pervade the debate.'
    st.markdown(why_caa)

# --- WHAT I DO ---
with st.container():
    V_SPACE(1)
    left_column, right_column = st.columns(2)
    with left_column:
        st.header('What we do')
        what_we_do = 'We work with policymakers at the bureaucratic and elected levels of municipal, provincial, and federal governments in Canada to find feasible, equitable pathways to decarbonizing energy in Canada. Our advocacy is fact based, using publicly available data to guide our policy recommendations.'
        st.write(what_we_do)
        st_lottie(meeting_json, width=350)
        st.header('Our areas of advocacy')
        areas_of_advocacy = '''
We advocate for clean power generation with nuclear power, and general electrification across industry, the economy, and society. Specific areas of focus are
* Electrification
* A Just Transition in energy and environment that maximizes worker well being while minimizing the environmental benefit of energy production and use.
* Ontario&#8217;s electricity transition (most innovation in Canada will occur in Ontario, so it&#8217;s important)
* Urban air quality
* Municipalities (they are where electrification will mostly occur)
* Energy and electricity forecasting

Learn more about these areas of focus by exploring the topics in the sidebar.
        '''
        st.markdown(areas_of_advocacy)
    with right_column:
        st.header('Who we are')
        who_we_are = '''
We are literally an alliance. We are a group of labour unions, led by the Canadian Nuclear Workers&#8217; Council, itself an umbrella organization representing labour unions across the Canadian nuclear sector.
        '''
        st.markdown(who_we_are)
        st.write('[Visit the CNWC&#8217;s website >](https://cnwc-cctn.ca/)')
        st.header('Our clean air vision')
        clean_air_vision = '''
Canadian households, businesses, and transport networks run on clean, quiet, affordable electricity, made in Canadian power plants by Canadian workers and Canadian equipment.
        '''
        st.markdown(clean_air_vision)
        st.header('Our clean air mission')
        clean_air_mission = '''
To be the premier voice for clean air through clean energy in Canada, in urban and rural areas, in workplaces and recreational spaces.

To put fact and data-driven cases to policymakers at Canadian municipal, provincial, and federal government levels, that provide guidance on how to meet clean air and climate change targets in the most proven and economically viable ways.

To promote the health of Canadians and the Canadian environment through proven, cost effective energy solutions.

To leverage our members&#8217; deep expertise, forged through decades of direct experience in Canada's most vital energy markets, to inform policymakers on viable ways to achieve environmental, economic, and societal goals.
        '''
        st.markdown(clean_air_mission)




# --- PROJECTS ---
#with st.container():
    #st.write('---')
    #st.header('Areas of advocacy')
    #st.write('##')
    #image_column, text_column = st.columns((1, 2))
    #with image_column:
        #st.write('waste waffle was here')
        ##st.image(waste_waffle)
    #with text_column:
        #st.markdown('### Clean Air Data')
        #st.markdown('***Canada&#8217;s industrial decarbonization*** presents opportunities for disruptive world leading economic transformation, with unprecedented greenhouse gas (GHG) emissions reductions. By far the main source of energy use and GHGs in Canada is from heat production, for large scale liquid-fuel feedstock manufacturing. This chiefly occurs in Alberta\'s oilsands, and the main energy usage, and GHG emissions source, is burning natural gas to provide heat and chemicals for the main stages of oilsands processing. These consist of separating bitumen from sand and manufacturing hydrogen.')
        #st.markdown('### The hydropower-from-Quebec issue')
        #st.markdown('***Gasoline powered personal motor transport*** is among the largest energy use categories of greenhouse gas (GHG) emissions in Canada. Decarbonizing this activity requires electrifying it. At the current usage level, this would require upward of 12,000 megawatts of new non-emitting electricity generating capacity across the country. This has the potential to eliminate some 85 million tons of GHGs annually from Canada&rdquo;s national inventory. Electrifying all road and rail transport could eliminate a further 60 million tons.')
        #st.markdown('### Municipalities as major energy centres')
        #st.markdown('***Urban electrification is proceeding*** in Canadian cities and towns, mostly at the smaller scale. Many ``off-grid'' applications currently dominated by two-stroke gasoline engines are seeing electric competitors in greater use. Chainsaws, augers, mowers, and other powered gardening equipment are examples. Electric bicycles and scooters, skateboards, and unicycles, are becoming ubiquitous.')
        #st.markdown('### Energy Forecasting')
        #st.markdown('***Urban electrification is proceeding*** in Canadian cities and towns, mostly at the smaller scale. Many ``off-grid'' applications currently dominated by two-stroke gasoline engines are seeing electric competitors in greater use. Chainsaws, augers, mowers, and other powered gardening equipment are examples. Electric bicycles and scooters, skateboards, and unicycles, are becoming ubiquitous.')
        #st.markdown('### Electrification')
        #st.markdown('***Urban electrification is proceeding*** in Canadian cities and towns, mostly at the smaller scale. Many ``off-grid'' applications currently dominated by two-stroke gasoline engines are seeing electric competitors in greater use. Chainsaws, augers, mowers, and other powered gardening equipment are examples. Electric bicycles and scooters, skateboards, and unicycles, are becoming ubiquitous.')
#


        #st.markdown('[Watch video...](https://www.youtube.com/watch?v=VqgUkExPvLY)')

# --- CONTACT FORM ---
#with st.container():
    # Define your javascript
    #my_js = """
    #alert("Hola mundo");
    #"""
    #
    ## Wrapt the javascript as html code
    #my_html = f"<script>{my_js}</script>"
    #
    ## Execute your app
    #st.title("Javascript example")
    #html(my_html)
    V_SPACE(1)
    st.header('Contact us')
    contact_form = """
    <form action="https://formsubmit.co/bwalker@cnwc-cctn.ca" method="POST">
     <input type="hidden" name="_captcha" value='false'>
     <input type="text" name="Your name" placeholder='Your name' required>
     <input type="email" name="Your email" placeholder='Your email' required>
     <textarea name='message' placeholder='Please type your message here' required></textarea>
     <button type="submit">Send</button>
</form>
    """

    left_col, right_col = st.columns(2)
    with left_col:
       st.markdown(contact_form, unsafe_allow_html=True)
    
