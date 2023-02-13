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
from bokeh.models import Span
from bokeh.models import HoverTool
from bokeh.models import LinearAxis, Range1d
from bokeh.models import NumeralTickFormatter
import os
path = os.path.dirname(__file__)
relative_path = '/data/'
path = os.path.dirname(__file__) #/var/www/html/etrak_site/pages
path_parent = os.path.dirname(path)
full_path = path_parent+relative_path


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

tableau_colors = ["#4e79a7","#f28e2c","#e15759","#76b7b2","#59a14f","#edc949","#af7aa1","#ff9da7","#9c755f","#bab0ab"]
tools=["pan,wheel_zoom,reset,save,xbox_zoom, ybox_zoom"] # bokeh web tools
endash = u'\u2013'
demand_color = '#1f77b4'
coal_color = '#e6550d'
wind_color = '#ff7f0e'


# --- EXIM AND GENOUTPUT DATA PREPROCESSING --
exim = pd.read_csv(full_path+'exim_ytd.csv')
exim = exim.set_index(pd.to_datetime(exim['datehour']))

dfs = pd.read_csv(full_path+'ieso_genoutputcap_v6.csv')# note version!
dfs = dfs.set_index(pd.to_datetime(dfs.iloc[:,0]))
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
print('gd_en_dt: ', gd_en_dt)
exim = exim.drop_duplicates()
en_dt = exim.tail(1).index.values[0]
en_dt = pd.to_datetime(en_dt)
print('en_dt: ', en_dt)
exim_matched = exim.loc[gd_st_dt:gd_en_dt] #########
exim_matched = exim.iloc[:, :-3].multiply(1)# in on_net_dem_svd.py this is multiplied by -1
del exim_matched['datehour']
exim_with_total = exim_matched.copy()
exim_with_total['total'] = exim_with_total.sum(axis=1)
gd = gd.join(exim_matched, how='inner')
# --- END OF EXIM, GENOUTPUT DATA PREPROCESSING ----

df = pd.read_csv(full_path+'exim_ytd.csv')
df = df.set_index(pd.to_datetime(df['datehour']))
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
        df = pd.read_csv(full_path+'exim_ytd.csv')
        df = df.set_index(pd.to_datetime(df['datehour']))
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
        
        years = ['2018', '2019', '2020', '2021', '2022']
        yl = len(years)
        
        p = figure(y_range=interties, x_range=(-9e13, 9e13), title="Ontario electricity exports (+) and imports ("+endash+"), Wh by year", tools=tools)
        
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
        p1.xaxis[0].formatter = DatetimeTickFormatter(months=['%b %d %y'], days=['%a %b %d'], hours=['%a %b %d\n%I%p'])
        p1.line(pd.to_datetime(df.loc[year_ny,'NEW-YORK'].resample(per).mean().index.values), df.loc[year_ny,'NEW-YORK'].resample(per).mean().values, line_color=tableau_colors[3])
        p1.circle(pd.to_datetime(df.loc[year_ny,'NEW-YORK'].resample(per).mean().index.values), df.loc[year_ny,'NEW-YORK'].resample(per).mean().values, fill_color=tableau_colors[3], line_color=tableau_colors[3])
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
        p1.xaxis[0].formatter = DatetimeTickFormatter(months=['%b %d %y'], days=['%a %b %d'], hours=['%a %b %d\n%I%p'])
        p1.line(pd.to_datetime(df.loc[year_mi,'MICHIGAN'].resample(per).mean().index.values), df.loc[year_mi,'MICHIGAN'].resample(per).mean().values, line_color=tableau_colors[3])
        p1.circle(pd.to_datetime(df.loc[year_mi,'MICHIGAN'].resample(per).mean().index.values), df.loc[year_mi,'MICHIGAN'].resample(per).mean().values, fill_color=tableau_colors[3], line_color=tableau_colors[3])
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
            p1.xaxis[0].formatter = DatetimeTickFormatter(months=['%b %d %y'], days=['%a %b %d'], hours=['%a %m/%d\n%I%p'])
            p1.line(pd.to_datetime(a.loc[year,intertie].resample(per).mean().index.values), a.loc[year,intertie].resample(per).mean().values, line_color=tableau_colors[3])
            p1.circle(pd.to_datetime(a.loc[year,intertie].resample(per).mean().index.values), a.loc[year,intertie].resample(per).mean().values, fill_color=tableau_colors[3], line_color=tableau_colors[3])
            hline = Span(location=0, dimension='width', line_color='black', line_width=3)
            p1.renderers.extend([hline])
            print('Que-HOOP-nuyr: ', a.loc['dec 30 2022', intertie])
            st.bokeh_chart(p1)

with tab5:
    sourceType = st.radio('Choose source/sink type', [s.title() for s in ['nuclear', 'non-nuclear baseload', 'ramping', 'peaking', 'dancers']], index=3, horizontal=True)
    unitTypes = open(full_path+'unit_classifications.json')
    unitTypes = json.load(unitTypes)
    unitType = unitTypes[sourceType.lower()]
    options = st.multiselect(
    'Choose your supply source(s)/sink(s)',
    unitType,
    unitType[0])
    

    col1a, col2a, col3a = st.columns([3, .5, 2.5], gap='large')

    with col1a:
        gd = gd.loc[gd_st_dt:en_dt]
        newdf = gd.copy()[options]
        newdf['Total'] = newdf.sum(axis=1)
        
        tdf = pd.read_csv(full_path+'zonedem_since_2003.csv')
        tdf = tdf.set_index(tdf.datehour)
        tdf.index = pd.to_datetime(tdf.index)
        del tdf['datehour']
        
        dems = tdf.loc[gd_st_dt:en_dt]
        netdem = dems['Zone Total'].subtract(solar.output)
        netdem = netdem.subtract(wind.output)
        
        x = netdem.index
        
        y = netdem.values
        y2 = newdf.Total.values
        
        title = 'Ontario net demand and sum of selected '+sourceType.title()+' sources/sinks. MW'
        pt = figure(title=title, x_range=(dems.index[0], dems.index[-1]), y_range=(0, dems['Ontario Demand'].max()), tools=tools)
        
        pt.line(x, y, color=tableau_colors[0], line_width=3)
        pt.yaxis.axis_label = 'Net demand'
        pt.yaxis.axis_label_text_color = tableau_colors[0]
        pt.yaxis.axis_label_text_font_style = 'bold'
        
        pt.extra_y_ranges = {"Dancers": Range1d(start=0, end=newdf.Total.max())}
        pt.line(x, y2, color=tableau_colors[1], y_range_name="Dancers", line_width=3)
        pt.add_layout(LinearAxis(y_range_name="Dancers", axis_label='Sum of net supply sources/sinks',
        axis_label_text_color=tableau_colors[1], axis_label_text_font_style='bold'), 'right')
        
        pt.xaxis[0].formatter = DatetimeTickFormatter(months=['%b %d %y'], days=['%a %b %d'], hours=['%a %m/%d\n%I%p'])
        
        hline = Span(location=0, dimension='width', line_color='black', line_width=3)
        pt.yaxis.formatter=NumeralTickFormatter(format='0,0')
        pt.yaxis[0].major_label_text_color = tableau_colors[0]
        pt.yaxis[1].major_label_text_color = tableau_colors[1]
        pt.yaxis[0].major_label_text_font_style = 'bold'
        pt.yaxis[1].major_label_text_font_style = 'bold'
        pt.renderers.extend([hline])
        st.bokeh_chart(pt)
    with col3a:
        with st.expander('See the demand data for the chart'):
            demand_data_blurb = '''
**Source**: [Independent Electricity System Operator Zonal demand](http://reports.ieso.ca/public/DemandZonal/)
            '''
            demand_data_blurb = demand_data_blurb
            st.markdown(demand_data_blurb)
            st.dataframe(dems.sort_index(ascending=True).style.format("{:,.0f}"))
        with st.expander('See the source/sink data for the chart'):
            source_data_blurb = '''
**Source**: [Independent Electricity System Operator GenoutputCapability](http://reports.ieso.ca/public/GenOutputCapability/)\n
[IESO export/import data](http://reports.ieso.ca/public/IntertieScheduleFlowYear/)
            '''
            st.markdown(source_data_blurb)
            st.dataframe(newdf.sort_index(ascending=True).style.format("{:,.0f}"))
