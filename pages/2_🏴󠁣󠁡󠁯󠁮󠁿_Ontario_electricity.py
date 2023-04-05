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
from bokeh.models import ColumnDataSource
from bokeh.palettes import GnBu3, OrRd3
from bokeh.plotting import figure, show
from bokeh.models import DatetimeTickFormatter
from streamlit_lottie import st_lottie
from bokeh.models import Span, Row, Column
from bokeh.models import HoverTool, MultiSelect
from bokeh.models import LinearAxis, Range1d
from bokeh.models import NumeralTickFormatter
from bokeh.models.widgets import RadioButtonGroup

from bokeh.models.callbacks import CustomJS
import os
path = os.path.dirname(__file__)
relative_path = '/data/'
path = os.path.dirname(__file__) #/var/www/html/etrak_site/pages
path_parent = os.path.dirname(path)
full_path = path_parent+relative_path

lead_double = u"\u201c"
follow_double = u"\u201d"
lead_single = u"\u2018"
follow_single = u"\u2019"


import urllib 
from bs4 import BeautifulSoup
import html

import json
from custom_modules import ieso
hover = HoverTool( # see https://docs.bokeh.org/en/test/docs/user_guide/tools.html
            tooltips=[
                ("datehour", "$datehour"),
                ("data (using $) (x,y)", "($x, $y)"),
                ("data (using @) (x,y)", "(@x, @y)"),
                ("canvas (x,y)", "($sx, $sy)")
                ],

    formatters={
        '$datehour'        : 'datetime'})

# https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title='Clean Air Alliance Ontario', page_icon=':sunflower:', layout='wide')

# --- LOAD ASSETS ---
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

#lightbulb_coding = load_lottieurl('https://assets4.lottiefiles.com/private_files/lf30_psn7xxju.json')
#tree_coding = load_lottieurl('https://assets4.lottiefiles.com/packages/lf20_BhbCTg.json')
#battery_coding = load_lottieurl('https://assets4.lottiefiles.com/packages/lf20_DwG3RkOkYV.json')
#heater_coding = load_lottieurl('https://assets8.lottiefiles.com/packages/lf20_FCYi2l.json')
#st_lottie(lightbulb_coding, width=200)

tableau_colors = ["#4e79a7","#f28e2c","#e15759","#76b7b2","#59a14f","#edc949","#af7aa1","#ff9da7","#9c755f","#bab0ab", "red", "blue"]
tools=["pan,wheel_zoom,reset,save,xbox_zoom, ybox_zoom"] # bokeh web tools
endash = u'\u2013'
demand_color = '#1f77b4'
coal_color = '#e6550d'
wind_color = '#ff7f0e'


# --- EXIM AND GENOUTPUT DATA PREPROCESSING --
exim = pd.read_csv(full_path+'exim_ytd.csv')
exim = exim.set_index(pd.to_datetime(exim['datehour']))

dfs = pd.read_json('http://canadianenergyissues.com/data/ieso_genoutputcap_v7.json')# note version!
print(dfs.head())
dfs = dfs.set_index(pd.to_datetime(dfs.datehour, unit='ms'))
dfs.index.name = 'datehour'

wind_solar_mask = ['wind', 'solar']
wind_solar_mask = dfs.fuel.str.contains('|'.join(wind_solar_mask), case=False)
dfs_nws = dfs[~wind_solar_mask] # nws = no wind, no solar
gd = dfs_nws.groupby([dfs_nws.index, 'unit']).mean().output.unstack()

solar = dfs[dfs['fuel']=='SOLAR']
wind = dfs[dfs['fuel']=='WIND']
g = lambda x: x.groupby(x.index).sum().output.to_frame()
wind = g(wind)
solar = g(solar)
gdws = dfs[wind_solar_mask].groupby([dfs[wind_solar_mask].index, 'unit']).mean().output.unstack() 
gd_st_dt = gd.index.get_level_values(0)[0]
gd_en_dt = gd.index.get_level_values(0)[-1]
exim = exim.drop_duplicates()
en_dt = exim.tail(1).index.values[0]
en_dt = pd.to_datetime(en_dt)
#exim_matched = exim.loc[gd_st_dt:gd_en_dt] #########
exim_matched = exim.iloc[:, :-3].multiply(1)# in on_net_dem_svd.py this is multiplied by -1
del exim_matched['datehour']
exim_with_total = exim_matched.copy()
exim_with_total['total'] = exim_with_total.sum(axis=1)
gd = gd.join(exim_matched, how='inner')
# --- END OF EXIM, GENOUTPUT DATA PREPROCESSING ----

df = pd.read_json('http://canadianenergyissues.com/data/exim_ytd.json')
print('df: ', df.head())
df = df.set_index(pd.to_datetime(df.index, unit='ms'))
pq = df.columns.str.contains('PQ')
pq_cols = df.loc[:,pq].columns[:-1]
a = df.copy()[pq_cols]
#df = df.copy().loc['January 1 2022':'december 31 2022', ['MICHIGAN', 'NEW-YORK', 'Quebec total']]
a_bokeh_cols = a.iloc[:, [0, 2, 3, 4, 5, 6]]

tab1, tab2, tab3, tab4, tab5 = st.tabs(['All Ontario', 'New York', 'Michigan', 'Quebec', 'Main providers'])

##### ALL ONTARIO TAB
with tab1:
    st.markdown('## Battery dreams: Ontario&#8217;s most important electricity supply sources and sinks include the neighbouring grids of Quebec, New York, and Michigan')
    battery_dreams_blurb = '''
Flows across the electrical interties with these neighbouring grids are vital to ensuring that Ontario electrical supply exactly matches net demand, every second of every minute of every day. The plot shows that New York, Michigan, and Quebec are by far the largest inter-jurisdictional transporters of electricity to and from Ontario. They are also among the top five biggest contributors to the shape of the province-wide net demand curve.

These facilities&mdash;along with some 32 Ontario hydro and gas-fired generating stations&mdash;perform the double duty of meeting elevated daily demand levels and &#8220;maneuvering&#8221; around intermittent renewable energy (wind and solar) output. Proponents of wind and solar claim batteries can also perform this duty.

Regardless of the veracity of that claim, the capital cost of battery storage is roughly $500 per kilowatt hour. In June 2022 through mid-September 2022, mean daily imports from Quebec across the main intertie were in the range 500 to 1000 MWh. Providing that level of energy with a combination of wind and solar and batteries, day in and day out for nearly 100 days straight, would require trillion-dollar investments.

With this in mind, the question becomes: for what purpose should these mostly publicly&ndash;owned assets utilize their amazing collective ability to vary power flow so that supply exactly matches demand every second of every minute? Should they use it to maneuver around erratic wind and solar output? Or should they use it to actually match demand? Under general electrification, demand will include new major (currently non-electrified) energy categories, mainly heating and transport.
    '''
    st.markdown(battery_dreams_blurb)

    col1, col2, col3 = st.columns([3, .5, 2.5], gap='large')
    #with col3:
        #st.markdown('## Ontario electricity imports and exports')
        #ontario_blurb = 'Ontario trades electrical power with three U.S. states and two Canadian provinces.'
        #st.write(ontario_blurb)

    ############# bokeh INTERTIE ANNUAL FLOW TOTALS ########################
    with col1:
        #df = pd.read_csv(full_path+'exim_ytd.csv')
        #df = df.set_index(pd.to_datetime(df['datehour']))
        all_interties = ['datehour', 'MANITOBA', 'MANITOBA SK', 'MICHIGAN', 'MINNESOTA',
        'NEW-YORK', 'PQ.AT', 'PQ.B5D.B31L', 'PQ.D4Z', 'PQ.D5A', 'PQ.H4Z',
        'PQ.H9A', 'PQ.P33C', 'PQ.Q4C', 'PQ.X2Y', 'Quebec total', 'PQ.AT_pos?',
        'Beau_pos?']
        
        interties = ['Manitoba', 'Manitoba SK', 'Minnesota','Michigan', 'New York', 'Quebec']
        df['ma_import'] = np.where(df['MANITOBA'] >=0, 0, df['MANITOBA'])
        df['ma_export'] = np.where(df['MANITOBA'] >=0, df['MANITOBA'], 0)
        df['mask_import'] = np.where(df['MANITOBA SK'] >=0, 0, df['MANITOBA SK'])
        df['mask_export'] = np.where(df['MANITOBA SK'] >=0, df['MANITOBA SK'], 0)
        df['mn_import'] = np.where(df['MINNESOTA'] >=0, 0, df['MINNESOTA'])
        df['mn_export'] = np.where(df['MINNESOTA'] >=0, df['MINNESOTA'], 0)
        df['mi_import'] = np.where(df['MICHIGAN'] >=0, 0, df['MICHIGAN'])
        df['mi_export'] = np.where(df['MICHIGAN'] >=0, df['MICHIGAN'], 0)
        df['ny_import'] = np.where(df['NEW-YORK'] >=0, 0, df['NEW-YORK'])
        df['ny_export'] = np.where(df['NEW-YORK'] >=0, df['NEW-YORK'], 0)
        df['qc_import'] = np.where(df['Quebec total'] >=0, 0, df['Quebec total'])
        df['qc_export'] = np.where(df['Quebec total'] >=0, df['Quebec total'], 0)
        imports = pd.concat([df['ma_import'], df['mask_import'], df['mn_import'], df['mi_import'], df['ny_import'], df['qc_import']], axis=1).multiply(1e6)
        imports.columns = interties
        
        exports = pd.concat([df['ma_export'], df['mask_export'], df['mn_export'], df['mi_export'], df['ny_export'], df['qc_export']], axis=1).multiply(1e6)
        exports.columns = interties
        exports = exports.groupby(exports.index.year).sum()
        imports = imports.groupby(imports.index.year).sum()
        exports.index = pd.Index([str(e) for e in exports.index.values])
        exports = exports.T
        imports.index = pd.Index([str(e) for e in imports.index.values])
        imports = imports.T
        
        imports.insert(0, 'Intertie', interties)
        exports.insert(0, 'Intertie', interties)
        imports.index = np.arange(0, 6)
        exports.index = np.arange(0, 6)
        
        years = ['2018', '2019', '2020', '2021', '2022', '2023']
        yl = len(years)
        
        p = figure(y_range=interties, x_range=(-9e13, 9e13), title="Ontario electricity exports (+) and imports ("+endash+"), Wh by year", tools=tools+['hover'], tooltips='$name: @Intertie: (@$name{0.000a})')
        
        p.hbar_stack(years, y='Intertie', height=0.9, color=tableau_colors[0:yl], source=ColumnDataSource(exports), legend_label=["%s exports" % x for x in years])
        
        p.hbar_stack(years, y='Intertie', height=0.9, color=tableau_colors[yl:], source=ColumnDataSource(imports),legend_label=["%s imports" % x for x in years])
        
        p.y_range.range_padding = 0.1
        p.ygrid.grid_line_color = tableau_colors[0]
        p.xgrid.grid_line_color = tableau_colors[0]
        #p.yaxis.axis_label_text_font_size = "20pt"
        p.xaxis.major_label_text_font_size = '14px'
        p.yaxis.major_label_text_font_size = '14px'
        p.title.text_font_size = '14px'
        p.legend.label_text_font_size = '15px'
        p.legend.location = "center_right"
        p.axis.minor_tick_line_color = tableau_colors[0]
        p.outline_line_color = None
        #p.sizing_mode='scale_both'
        st.bokeh_chart(p)
    with col3:
   #st.header('Total imports/exports by year')
   #st.write('Note the differences')
        top_5_blurb = '''
        As you can see, Quebec exports by far the most electricity to Ontario. In fact, two of the top-five contributors to net demand mentioned above are Quebec interties (see the Quebec tab for details). As net demand is demand minus wind and solar output, these interties play a critical role, arguably the most important role, in balancing variable renewable output.
        
        Flows between Ontario and Quebec are highly dependent on time of day and season. Generally, imports from Quebec mostly occur during daylight hours, and exports to Quebec mostly during &#8220;off-peak&#8221; hours.
        '''
        st.markdown(top_5_blurb)
with tab2:
    st.header('New York')
    st.write('New York is Ontario&#8217;s second largest electricity export market.')
    res = ['60T', 'D', 'W', 'M']
    res_in_english = ['Hourly', 'Daily', 'Weekly', 'Monthly']
    mtick_factor = [1.5e3, 61 , 9, 1]
    year_list = ['2023', '2018', '2019', '2020', '2021', '2022']

    col1, col2, col3 = st.columns([3, .5, 2.5], gap='large')
    with col3:
        year_ny = st.selectbox(label = "Choose a year", options = year_list, label_visibility='collapsed', key='nysb1')
        period_ny = st.selectbox(label = "Choose a period", options = res_in_english, label_visibility='collapsed', key='nysb2')

    with col1:
        per = res[res_in_english.index(period_ny)]
        p1 = figure(title='New York '+year_ny+', '+res_in_english[res_in_english.index(period_ny)], tools=tools)
        p1.xaxis[0].formatter = DatetimeTickFormatter(months=['%b %d %y'], days=['%a %b %d'], hours=['%a %b %d %I%p'])
        p1.line(pd.to_datetime(df.loc[year_ny,'NEW-YORK'].resample(per).mean().index.values), df.loc[year_ny,'NEW-YORK'].resample(per).mean().values, line_color=tableau_colors[3])
        p1.circle(pd.to_datetime(df.loc[year_ny,'NEW-YORK'].resample(per).mean().index.values), df.loc[year_ny,'NEW-YORK'].resample(per).mean().values, fill_color=tableau_colors[3], line_color=tableau_colors[3])
        p1.xaxis.major_label_orientation = 0.5
        hline = Span(location=0, dimension='width', line_color='black', line_width=3)
        p1.renderers.extend([hline])
        st.bokeh_chart(p1)

with tab3:
    st.header('Michigan')
    st.write('Michigan is Ontario&#8217;s largest electricity export market.')
    res = ['60T', 'D', 'W', 'M']
    res_in_english = ['Hourly', 'Daily', 'Weekly', 'Monthly']
    mtick_factor = [1.5e3, 61 , 9, 1]
    year_list = ['2023', '2018', '2019', '2020', '2021', '2022']
    
    col1, col2, col3 = st.columns([3, .5, 2.5], gap='large')
    with col3:
        year_mi = st.selectbox(label = "Choose a year", options = year_list, label_visibility='collapsed', key='misb1')
        period_mi = st.selectbox(label = "Choose a period", options = res_in_english, label_visibility='collapsed', key='misb2')
    
    with col1:
        per = res[res_in_english.index(period_mi)]
        p1 = figure(title='Michigan '+year_mi+', '+res_in_english[res_in_english.index(period_mi)], tools=tools)
        p1.xaxis[0].formatter = DatetimeTickFormatter(months=['%b %d %y'], days=['%a %b %d'], hours=['%a %b %d %I%p'])
        p1.line(pd.to_datetime(df.loc[year_mi,'MICHIGAN'].resample(per).mean().index.values), df.loc[year_mi,'MICHIGAN'].resample(per).mean().values, line_color=tableau_colors[3])
        p1.circle(pd.to_datetime(df.loc[year_mi,'MICHIGAN'].resample(per).mean().index.values), df.loc[year_mi,'MICHIGAN'].resample(per).mean().values, fill_color=tableau_colors[3], line_color=tableau_colors[3])
        p1.xaxis.major_label_orientation = 0.5
        hline = Span(location=0, dimension='width', line_color='black', line_width=3)
        p1.renderers.extend([hline])
        st.bokeh_chart(p1)

with tab4:
    cola, colb = st.columns(2)
    with cola:
        st.markdown('### Quebec cannot provide Ontario with 24/7 power to replace Ontario nuclear plants')
        st.markdown('In spite of claims to the contrary, Quebec does not possess the generation capacity to become a major bulk provider of electricity to Ontario on the scale of multiples of thousands of megawatts. Nor does Quebec possess the desire to export power at this scale at low cost, a key Ontario requirement in such a scenario. Quebec&#8217;s electrical relationship with Ontario is complex, is highly dependent on the time of day, and involves exports as well as imports.')
        
        st.markdown('### Most Quebec homes are heated electrically')
        st.markdown('On cold days, Quebec heat demand can approach 20,000 megawatts. That is roughly equivalent to total Ontario electrical demand on cold days. If Ontario were to increase its demand for Quebec electricity, Quebec homes would face a shortage of heating &#8220;fuel.&#8221; Of course, this will never happen. Quebec would never prioritize electricity exports over its internal domestic demand.')
        st.markdown('### Quebec has major electrification plans')
        st.markdown('From EVs to a significantly expanded Montreal Metro system, to electric high-speed rail connections with Ontario, Quebec&#8217;s electrical demand is set to skyrocket.')
    with colb:
        st.markdown('### Two of the top five most important contributors to the shape of Ontario&rsquo;s net demand curve are Quebec interties. The Ooutaouais Intertie (PQ.AT) is by far the most important of all.')
        st.markdown('Quebec&rsquo;s importance in shaping net demand (demand minus wind and solar) is due in large part to the impact of wind and solar as random sources of supply largely uncorrelated with demand. \nThe plots below show the hourly flows across the Quebec interties. Note PQ.AT&mdash;it is the single most important contributor to Ontario&rsquo;s net demand curve shape. If you zoom in on the left-hand plot, you can see that even in the dead of summer&mdash;when Quebec imports to Ontario are at their highest&mdash;flow often changes direction twice per day.')
        st.markdown('### Flows across the Quebec, New York, and Michigan interties, and output from Ontario gas and hydro plants, including those on the Ottawa and Madawaska River systems, almost exactly trace the Ontario net demand curve.')
        st.markdown('This is because these facilities&rsquo; duties include meeting Ontario demand ***and*** balancing wind and solar output in southern Otnario. If wind and solar capacity in southern Ontario were increased, there would be greater need for &#8220;balancing&#8221; sources like the Quebec interties and the eastern Ontario hydro plants. Suggesting that Quebec&rsquo;s hydroelectric system can act as Ontario&rsquo;s &#8220;battery&#8221; in order to complement Ontario wind and solar neglects to consider Quebec&rsquo;s role as balancer of the Ontario&rsquo;s ***current*** wind and solar fleets.')
    with cola:
        st.markdown('### The &#8220;dancers&#8221; of Ontario perform the role today that storage will theoretically perform in the future: balancing erratic VRE output')

    st.markdown('### Quebec intertie data')
    col1, col2, col3 = st.columns([3, .5, 2.5], gap='large')
    res = ['60T', 'D', 'W', 'M']
    res_in_english = ['Hourly', 'Daily', 'Weekly', 'Monthly']
    mtick_factor = [1.5e3, 61 , 9, 1]
    year_list = ['2023', '2018', '2019', '2020', '2021', '2022']
    
    with col3:
        intertie = st.selectbox(label = "Choose an intertie", options = pq_cols, label_visibility='collapsed')
        year = st.selectbox(label = "Choose a year", options = year_list, label_visibility='collapsed')
        period = st.selectbox(label = "Choose a period", options = res_in_english, label_visibility='collapsed')
        
        qc_fig, axs = plt.subplots(3, 3, figsize=(7, 5), sharex=True, sharey='row')
        axes_list = [item for sublist in axs for item in sublist ]
        title = f"{intertie} {year}"
        for col in pq_cols:
            per = res[res_in_english.index(period)]
            mtf = mtick_factor[res_in_english.index(period)]
            ax = axes_list.pop(0)
            #a[col].loc[year].resample(per).mean().plot(ax=ax, color=tableau_colors[3])
            ax.plot(a[col].loc[year].resample(per).mean().index, a[col].loc[year].resample(per).mean().values, color=tableau_colors[3])
            ax.set_xlabel('')
            ax.set_title(col)
            ax.grid()
            ax.axhline(0, color='k')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
            for xl in ax.get_xticklabels():
                xl.set_rotation(30)
                xl.set_ha('right')
            #ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
            #ax.fmt_xdata = mdates.DateFormatter('%m-%d')
            #ax.xaxis.set_major_locator(mtick.MultipleLocator(mtf))
            sns.despine()
        plt.subplots_adjust(hspace=.3)
        container1 = st.container()
        qc_fig
        ##################### BOKEH INTERTIE LINEPLOT ##################
    with col1:
            per = res[res_in_english.index(period)]
            p1 = figure(title=intertie+' '+year+', '+res_in_english[res_in_english.index(period)], tools=tools)
            p1.xaxis[0].formatter = DatetimeTickFormatter(months=['%b %d %y'], days=['%a %b %d'], hours=['%a %m %d %I%p'])
            p1.line(pd.to_datetime(a.loc[year,intertie].resample(per).mean().index.values), a.loc[year,intertie].resample(per).mean().values, line_color=tableau_colors[3])
            p1.circle(pd.to_datetime(a.loc[year,intertie].resample(per).mean().index.values), a.loc[year,intertie].resample(per).mean().values, fill_color=tableau_colors[3], line_color=tableau_colors[3])
            p1.xaxis.major_label_orientation = 0.5
            hline = Span(location=0, dimension='width', line_color='black', line_width=3)
            p1.renderers.extend([hline])
            st.bokeh_chart(p1)

with tab5:
    st.markdown('### Which sources/sinks contribute most to the shape of net demand?')
    valuable_gen_blurb = '''
    The plot below shows all 20+ megawatt individual sources and sinks of electrical power on the southern Ontario grid (all reporting entities east of the [IESO&#8217;s northwest zone](https://www.ieso.ca/localContent/zonal.map/index.html)). You can select any combination of individual sources/sinks in each category.
    
    The sources/sinks in the &ldquo;dancers &rdquo; category perform today what variable renewable energy (VRE) proponents claim that storage&mdash;by which they usually mean chemical batteries&mdash;will perform in an all-VRE grid. As you can see, the &ldquo;dancers &rdquo; comprise nearly 12,000 MW of &ldquo;capacity &rdquo;. Battery storage today costs upward of \$500 per kWh.
    
    For 12,000 MW of capacity to run for one hour would require at least \$6 billion worth of batteries, for 2 hours \$12 billion worth; and for 10 hours, \$60 billion. 

    During winter, when Ontario needs the most energy, there are often wind lulls lasting many hours, sometimes days. Solar photovoltaic output is low, and on cloudy days minimal&mdash;and of course during nighttime it is always zero. Batteries would have to be sized so as to be capable of outputting many thousands of megawatts of power, for days on end. Battery storage costs would push into the hundreds of billions, even trillions, of dollars.

    A grid dominated by VRE-plus-storage is simply not financially viable.
    
    '''
    math_str = '''
    $ x = {-b \pm \sqrt{b^2-4ac} \over 2a} $
    '''
    st.markdown(valuable_gen_blurb)

#    sourceType = st.radio('Choose source/sink type', [s.title() for s in ['nuclear', 'non-nuclear baseload', 'ramping', 'peaking', 'dancers']], index=4, horizontal=True)
#    unitTypes = open(full_path+'unit_classifications.json')
#    unitTypes = json.load(unitTypes)
#    unitType = unitTypes[sourceType.lower()]
#    options = st.multiselect(
#    'Choose your supply source(s)/sink(s)',
#    unitType,
#    unitType[0])
    


    exim = pd.read_json('http://canadianenergyissues.com/data/exim_ytd.json')
    exim = exim.set_index(pd.to_datetime(exim.index, unit='ms'))
    
    dfs = dfs.copy()
    dfs['datehour'] = pd.to_datetime(dfs.datehour, unit='ms')
    dfs = dfs.set_index('datehour')
    dfs['datehour'] = dfs.index
    
    wind_solar_mask = ['wind', 'solar']
    wind_solar_mask = dfs.fuel.str.contains('|'.join(wind_solar_mask), case=False)
    dfs_nws = dfs[~wind_solar_mask] # nws = no wind, no solar
    gd = dfs_nws.groupby([dfs_nws.index, 'unit']).mean().output.unstack()
    
    solar = dfs[dfs['fuel']=='SOLAR']
    wind = dfs[dfs['fuel']=='WIND']
    g = lambda x: x.groupby(x.index).sum().output.to_frame()
    wind = g(wind)
    solar = g(solar)
    gdws = dfs[wind_solar_mask].groupby([dfs[wind_solar_mask].index, 'unit']).mean().output.unstack() 
    gd_st_dt = pd.to_datetime(gd.index.get_level_values(0)[0], unit='ms')
    gd_en_dt = pd.to_datetime(gd.index.get_level_values(0)[-1], unit='ms')
    exim = exim.drop_duplicates()
    en_dt = exim.tail(1).index.values[0]
    en_dt = pd.to_datetime(en_dt)
    print(exim.tail())
    print('matched datetimes: gd_en_dt TYPE is ', type(gd_en_dt), ', and exim TYPE is: ', type(exim.tail(1).index[0]))
    #exim_matched = exim.loc[gd_st_dt:gd_en_dt] #########
    exim_matched = exim.iloc[:, :-3].multiply(1)# in on_net_dem_svd.py this is multiplied by -1
    print(exim_matched.tail())
    #del exim_matched['datehour']
    
    exim_with_total = exim_matched.copy()
    exim_with_total['total'] = exim_with_total.sum(axis=1)
    gd = gd.join(exim_matched, how='inner')
    print(gd.tail())
    # --- END OF EXIM, GENOUTPUT DATA PREPROCESSING ----
    
    pq = exim.columns.str.contains('PQ')
    pq_cols = exim.loc[:,pq].columns[:-1]
    a = exim.copy()[pq_cols]
    #df = df.copy().loc['January 1 2022':'december 31 2022', ['MICHIGAN', 'NEW-YORK', 'Quebec total']]
    a_bokeh_cols = a.iloc[:, [0, 2, 3, 4, 5, 6]]
    
    unitTypes = open(path_parent+'/data/unit_classifications_final_southern.json')
    unitTypes = json.load(unitTypes)
    sourceType = ['nuclear', 'non-nuclear baseload', 'ramping', 'peaking', 'dancers']
    
    gd = gd.loc[gd_st_dt:en_dt]
    newdf = gd.copy()
    newdf['Total'] = newdf.sum(axis=1)
    
    tdf = pd.read_json('http://canadianenergyissues.com/data/zonedem_since_2003.json')
    #tdf = tdf.set_index(tdf.datehour)
    tdf.index = pd.to_datetime(tdf.index)
    #del tdf['datehour']
    
    dems = tdf.loc[gd_st_dt:en_dt]
    dems.loc[:, 'Zone_total_less_northwest'] = dems.loc[:, 'Zone Total'].subtract(dems.loc[:, 'Northwest'])
    
    netdem = dems['Zone_total_less_northwest'].subtract(solar.output)
    netdem = netdem.subtract(wind.output).to_frame()
    netdem['datehour'] = netdem.index
    netdem.columns = ['demand', 'datehour']
    netdem.index = np.arange(0, netdem.shape[0])
    dem_source = ColumnDataSource(data=netdem)
    new_newdf = newdf.copy()
    new_newdf['datehour'] = new_newdf.index
    new_newdf['total'] = new_newdf.Total.values
    new_newdf.index = np.arange(0, new_newdf.shape[0])
    
    sourceSink_source = ColumnDataSource(data=new_newdf)
    sourceSink_source2 = ColumnDataSource(data=new_newdf)
    
    x = netdem.index
    
    y = netdem.values
    y2 = newdf.Total.values
    
    tools=["pan,wheel_zoom,reset,save,xbox_zoom, ybox_zoom"] # bokeh web tools
    
    tableau_colors = ["#4e79a7","#f28e2c","#e15759","#76b7b2","#59a14f","#edc949","#af7aa1","#ff9da7","#9c755f","#bab0ab", "red", "blue"]
    
    #title = 'Ontario net demand and sum of selected '+sourceType.title()+' sources/sinks. MW'
    title = 'Ontario '+lead_double+'southern'+follow_double+' grid net demand and sum of selected sources/sinks, MW'
    pt = figure(title=title, x_range=(dems.index[0], dems.index[-1]), y_range=(0, dems['Ontario Demand'].max()), min_border_left=-4, tools=tools)
    
    pt.line('datehour', 'demand', source=dem_source, color='black', line_width=3)
    pt.yaxis.axis_label = 'Net demand'
    pt.yaxis.axis_label_text_color = 'black'
    pt.yaxis.axis_label_text_font_style = 'bold'
    
    r = Range1d(start=0, end=new_newdf.total.max())
    pt.extra_y_ranges = {"Dancers": r}
    pt.line('datehour', 'total', source=sourceSink_source, color='red', y_range_name="Dancers", line_width=3)
    pt.add_layout(LinearAxis(y_range_name="Dancers", axis_label='Sum of net supply sources/sinks',
    axis_label_text_color='red', axis_label_text_font_style='bold'), 'right')
    
    pt.xaxis[0].formatter = DatetimeTickFormatter(months=['%b %d %y'], days=['%a %b %d'], hours=['%a %m %d %I%p'])
    
    hline = Span(location=0, dimension='width', line_color='black', line_width=3)
    pt.yaxis.formatter=NumeralTickFormatter(format='0,0')
    pt.yaxis[0].major_label_text_color = 'black'
    pt.yaxis[1].major_label_text_color = 'red'
    pt.yaxis[0].major_label_text_font_style = 'bold'
    pt.yaxis[1].major_label_text_font_style = 'bold'
    pt.renderers.extend([hline])
    
    rbv = ''
    options = unitTypes['dancers']
    multiselect = MultiSelect(title = 'Choose one or more sources/sinks', value = [], options = options, sizing_mode='stretch_height', width_policy='min')
    a = RadioButtonGroup(active=4, labels=sourceType, orientation='horizontal', aspect_ratio='auto', sizing_mode='stretch_height')
    callback2 = CustomJS(args={'multiselect':multiselect,'unitTypes':unitTypes, 'a':a}, code="""
    const val = a.active;
    const lab = a.labels;
    const sourceType = lab[val];
    multiselect.options=unitTypes[sourceType];
    console.log('wh-options: ', multiselect.options);
    console.log(val, sourceType);
    """)
    
    callback = CustomJS(args = {'sourceSink_source': sourceSink_source, 'sourceSink_source2': sourceSink_source2, 'r': r, 'unitTypes':unitTypes,'a':a, 'options':multiselect.options, 's':multiselect},
    code = """
    function sum(arrays) {
    return arrays.reduce((acc, array) => acc.map((sum, i) => sum + array[i]), new Array(arrays[0].length).fill(0));
    }
    options.value = unitTypes[a.value];
    console.log('options dude hey: ', options);
    const are = r;
    console.log('are: ', are);
    var data = sourceSink_source.data;
    var data2 =sourceSink_source2.data;
    console.log(data['datehour']);
    var select_sourcesSinks = cb_obj.value;
    const arr = [];
    select_sourcesSinks.forEach((key) => {
    arr.push(data2[key]);
    });
    const newSource = {'datehour': data2['datehour']};
    newSource['total'] = sum(arr);
    const newMin = Math.min(...newSource['total']);
    const newMax = Math.max(...newSource['total']);
    are.start=newMin;
    are.end=newMax;
    sourceSink_source.data = newSource;
    """)
    
    multiselect.js_on_change('value', callback)
    a.js_on_click(callback2) 
    pt.xaxis.major_label_orientation = 0.5
    pt.sizing_mode='scale_height'
    layout = Row(pt, multiselect)
    layout2 = Column(a, layout)
    st.bokeh_chart(layout2)
    st.markdown('### What is gained by prioritizing VRE, when it requires fast-responding sources/sinks?')
    vre_drawbacks = '''
    The &#8220;dancers&#8221; category in the plot above includes interties, hydro plants, and gas plants. Unless the generators are all hydro (or some non-emitting dispatchable generation), then VRE ***requires*** fossil generation. 

    And in cases where &#8220;dancers&#8221; are indeed all non-emitting, then what environmental benefit is gained with VRE? 
    '''
    st.markdown(vre_drawbacks)
    st.markdown('### The under-appreciated value of baseload supply')
    baseload_advantages = '''
    Peak demand conditions get most of the attention in discussions about grid planning. Often the value of baseload supply is lost in these discussions. But baseload is like air&mdash;we need it every second of every minute of every day, and if were not provided for one second, we would notice.

    From the plot above, you can see that nuclear provides nearly all Ontario's baseload supply. Because nuclear generates power without emissions, we can think of it as a clean air air supply.
    '''

        #with st.expander('See the demand data for the chart'):
            #demand_data_blurb = '''
#**Source**: [Independent Electricity System Operator Zonal demand](http://reports.ieso.ca/public/DemandZonal/)
            #'''
            #demand_data_blurb = demand_data_blurb
            #st.markdown(demand_data_blurb)
            #st.dataframe(dems.sort_index(ascending=True).style.format("{:,.0f}"))
        #with st.expander('See the source/sink data for the chart'):
            #source_data_blurb = '''
#**Source**: [Independent Electricity System Operator GenoutputCapability](http://reports.ieso.ca/public/GenOutputCapability/)\n
#[IESO export/import data](http://reports.ieso.ca/public/IntertieScheduleFlowYear/)
            #'''
            #st.markdown(source_data_blurb)
            #st.dataframe(newdf.sort_index(ascending=True).style.format("{:,.0f}"))
