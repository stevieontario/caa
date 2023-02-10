from PIL import Image
import streamlit as st
import requests
import numpy as np
import pandas as pd
from streamlit_lottie import st_lottie
import json
from bokeh.layouts import gridplot
tableau_colors = ["#4e79a7","#f28e2c","#e15759","#76b7b2","#59a14f","#edc949","#af7aa1","#ff9da7","#9c755f","#bab0ab"]
fc = '/var/www/html/cleanair/images/forecast.json'


import os
path = os.path.dirname(__file__)
relative_path = '/data/'
path = os.path.dirname(__file__) #/var/www/html/etrak_site/pages
path_parent = os.path.dirname(path)
full_path = path_parent+relative_path

endash = u'\u2013'
minus_sign = u'\u2212'

tools=["pan,wheel_zoom,box_zoom,reset,save, ybox_zoom"]
# https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title='Clean Air Alliance Forecasting', page_icon='📈', layout='wide')

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
forecasting_coding = load_lottieurl('https://assets1.lottiefiles.com/packages/lf20_ewssaiig.json')

# --- DATA DEFS ---
def temp_ranges(x):
    if x < -20:
        return '< '+minus_sign+'20°'
    elif -20 <= x < -10:
        return minus_sign+'20° to\n'+minus_sign+'11°'
    elif -10 <= x < 0:
        return minus_sign+'10° to\n'+minus_sign+'1°'
    elif 0 <= x < 10:
        return '0°'+endash+'9°'
    elif 10 <= x < 20:
        return '10°'+endash+'19°'
    elif 20 <= x < 30:
        return '20°'+endash+'29°'
    else:
        return '> 29°'

# --- WHAT I DO ---
with st.container():
    col1, col2 = st.columns([ 1, 3])
    with col1:
        st_lottie(forecasting_coding, width=200)
    with col2:
        st.markdown('## Energy forecasting will be electricity forecasting&mdash;with less margin for error')
    col1, col2 = st.columns(2, gap='large')
    with col1:
        #st.markdown('### What will electrical demand look like as the economy is electrified?')
        #forecasting_blurb = '**_New demand curve_** Most electrical demand curves appear similar in shape, reflecting daily work cycles (see the plot). The biggest drivers of current electrical demand are hour of day and day of week. Outdoor temperature is important, but not as much as the first two. But with electrification of transport and heating, this will change. When heat is provided with electricity, outdoor temperature will be the single largest factor in electrical demand.'
        #st.markdown(forecasting_blurb)
        st.markdown('### Electrification will increase range of demand')
        forecasting_blurb = '**_Toronto electrical demand_**, shown below, has since 2002 occurred within fairly narrow and predictable ranges. However, electrification will increase those ranges. Since 2002, outlier demand values&mdash;values that are abnormally distant from most other values&mdash;have fallen within a manageable 1,000&ndash;1,500 MW range. With electrification, these ranges will increase, by as much as 5,000 megawatts, perhaps more. Managing these sharp demand swings will be a challenge for both the municipal LDC (Toronto Hydro) and the Ontario system operator.'
        st.markdown(forecasting_blurb)
        import iqplot
        
        tdf = pd.read_csv(full_path+'zonedem_since_2003.csv')
        weath = pd.read_csv(full_path+'weather_since_2003.csv')
        tdf = tdf.set_index(tdf.datehour)
        tdf.index = pd.to_datetime(tdf.index)
        tdf = tdf.copy().loc['may 1 2003 1 a.m.':'september 30 2022']
        del tdf['datehour']
        weath = weath.set_index(weath.datehour)
        del weath['datehour']
        weath.index = pd.to_datetime(weath.index)
        weath.columns = ['temp', 'dptemp']
        weath = weath.copy().loc['may 1 2003':]
        tdf = tdf.join(weath, on=tdf.index).dropna()
        
        hols = ['jan 1 2003', 'apr 18 2003', 'may 19 2003', 'jul 1 2003', 'aug 4 2003', 'sep 1 2003', 'oct 13 2003', 'dec 25 2003',
        'jan 1 2004', 'apr 9 2004', 'may 24 2004', 'jul 1 2004', 'aug 2 2004', 'sep 6 2004', 'oct 11 2004', 'dec 27 2004',
        'jan 3 2005', 'mar 25 2005', 'may 23 2005', 'jul 1 2005', 'aug 1 2005', 'sep 5 2005', 'oct 10 2005', 'dec 26 2005',
        'jan 2 2006', 'apr 14, 2006', 'may 22 2006', 'jul 1 2006', 'aug 7 2006', 'sep 4 2006', 'oct 9 2006', 'dec 25 2006',
        'jan 1 2007', 'apr 6 2007', 'may 21 2007', 'jul 2 2007', 'aug 6 2007', 'sep 3 2007', 'oct 8 2007', 'dec 25 2007',
        'jan 1 2008', 'feb 18 2008', 'mar 21 2008', 'may 19 2008', 'jul 1 2008', 'aug 4 2008', 'sep 1 2008', 'oct 13 2008', 'dec 25 2008',
        'jan 1 2009', 'feb 16 2009', 'apr 10 2009', 'may 18 2009', 'jul 1 2009', 'aug 3 2009', 'sep 7 2009', 'oct 12 2009', 'dec 25 2009',
        'jan 1 2010', 'feb 15 2010', 'apr 2 2010', 'may 24 2010', 'jul 1 2010', 'aug 2 2010', 'sep 6 2010', 'oct 11 2010', 'dec 27 2010',
        'jan 3 2011', 'feb 21 2011', 'apr 22 2011', 'may 23 2011', 'jul 1 2011', 'aug 1 2011', 'sep 5 2011', 'oct 10 2011', 'dec 26 2011',
        'jan 2 2012', 'feb 20 2012', 'apr 6 2012', 'may 21 2012', 'jul 2 2012', 'aug 6 2012', 'sep 3 2012', 'oct 8 2012', 'dec 25 2012',
        'jan 1 2013', 'feb 18 2013', 'mar 29 2013', 'may 20 2013', 'jul 1 2013', 'aug 5 2013', 'sep 2 2013', 'oct 14 2013', 'dec 25 2013',
        'jan 1 2014', 'feb 17 2014', 'apr 18 2014', 'may 19 2014', 'jul 1 2014', 'aug 4 2014', 'sep 1 2014', 'oct 13 2014', 'dec 25 2014',
        'jan 1 2015', 'feb 16 2015', 'apr 3 2015', 'may 18 2015', 'jul 1 2015', 'aug 3 2015', 'sep 7 2015', 'oct 12 2015', 'dec 25 2015',
        'jan 1 2016', 'feb 15 2016', 'mar 25 2016', 'may 23 2016', 'jul 1 2016', 'aug 1 2016', 'sep 5 2016', 'oct 10 2016', 'dec 26 2016',
        'jan 2 2017', 'feb 20 2017', 'apr 14 2017', 'may 22 2017', 'jul 1 2017', 'aug 7 2017', 'sep 4 2017', 'oct 9 2017', 'dec 25 2017',
        'jan 1 2018', 'feb 19 2018', 'mar 30 2018', 'may 21 2018', 'jul 2 2018', 'aug 6 2018', 'sep 3 2018', 'oct 8 2018', 'dec 25 2018',
        'jan 1 2019', 'feb 18 2019', 'apr 19 2019', 'may 20 2019', 'jul 1 2019', 'aug 5 2019', 'sep 2 2019','oct 14 2019', 'dec 25 2019',
        'jan 1 2020', 'feb 17 2020', 'apr 10 2020', 'may 18 2020', 'jul 1 2020', 'aug 3 2020', 'sep 7 2020', 'oct 12 2020', 'dec 25 2020',
        'jan 1 2021', 'feb 15 2021', 'apr 2 2021', 'may 24 2021', 'jul 1 2021', 'aug 2 2021', 'sep 6 2021', 'oct 11 2021', 'dec 25 2021',
        'jan 3 2022', 'feb 21 2022', 'apr 15 2022', 'may 23 2022', 'jul 1 2022', 'aug 1 2022', 'sep 5 2022', 'oct 10 2022', 'dec 25 2022']
        hols = pd.to_datetime(hols)
        import itertools
        hols = list(itertools.chain.from_iterable([pd.date_range(h, periods=24, freq='60T').strftime('%Y-%m-%d %H:00:00').tolist() for h in hols]))
        hols = pd.DatetimeIndex(hols[1:])
        tdf['hol'] = np.where(tdf.index.isin(hols), 1, 0)
        weather_pred = np.array([-1, 0, 1, 1, 1, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -2, -2, -3, -3, -3, -2, 0, 1, 2, 3, 3, 3, 3, 2, 1, -1, -2, -3, -3, -4, -5, -5, -6, -6, -6, -6, -6, -6, -5, -4, -3, -2, 0, 1, 1, 1, 1, 1, 1, 0, -1, -2, -3, -3, -3, -2, -2, -2, -1, -1, 0, 0, 1, 2, 2, 3, 4])
        
        rd_ind = pd.date_range('2022-11-22 12:00:00', '2022-11-25', periods=weather_pred.shape[0]) #rd = real data
        pred_df = pd.DataFrame(weather_pred, index=rd_ind, columns=['temp'])
        pred_df['hol'] = np.where(pred_df.index.isin(hols), 1, 0)
        
        # TRAIN/TEST split -- based on tutorial at https://youtu.be/vV12dGe_Fho
        train = tdf.loc[tdf.index < '2015-01-01 00:00:00']
        test = tdf.loc[tdf.index >= '2015-01-01 00:00:00']
        
        def add_features(df, zone):
            """
            create features mostly based on pd.DateTimeIndex, but also weather-related.
            
            """
            d = df[zone].copy().to_frame()
            d['hr'] = d.index.hour
            d['day'] = d.index.day
            d['dow'] = d.index.dayofweek
            d['dow'] = np.where(df['hol']==1, 7, d['dow'])
            d['qtr'] = d.index.quarter
            d['mo'] = d.index.month
            d['temp'] = df.temp
            return d
        
        train = add_features(train, 'Toronto').astype(int)
        test = add_features(test, 'Toronto').astype(int)
        train['dayname'] = train.index.day_name()
        train['dayname'] = np.where(train.dow==7, 'Holiday', train.dayname)
        train['dayname'] = [val[:3] for val in train['dayname'].values]
        train['Temp range'] = train['temp'].apply(temp_ranges)
        train = train.copy().sort_values('dow', ascending=True)
        p1_box = iqplot.box(        data=train,
        cats='dayname',
        q ='Toronto',
        q_axis='y',
        whisker_caps=True,
        outlier_marker='diamond',
        outlier_kwargs=dict(size=10, color=tableau_colors[3]),
        box_kwargs=dict(fill_color=tableau_colors[2], width=.75),
        whisker_kwargs=dict(line_color='#7C0000', line_width=3),
        toolbar_location = 'right',
        tools=tools,
        title="Toronto electricity demand by day of week, 2002"+endash+"2015"
        )
        p1_box.yaxis.axis_label = 'MW'
        train_hr_sorted = train.copy().sort_values('hr')
        train_temp_sorted = train.copy().sort_values('temp')
        p2_box = iqplot.box(        data=train_hr_sorted,
        cats='hr',
        q ='Toronto',
        q_axis='y',
        whisker_caps=True,
        outlier_marker='diamond',
        outlier_kwargs=dict(size=10, color=tableau_colors[3]),
        box_kwargs=dict(fill_color=tableau_colors[2], width=.75),
        whisker_kwargs=dict(line_color='#7C0000', line_width=3),
        toolbar_location = 'right',
        tools=tools,
        title="Toronto electricity demand by hour of day, 2002"+endash+"2015"
        )
        p2_box.yaxis.axis_label = 'MW'
        p3_box = iqplot.box(        data=train_temp_sorted,
        cats='Temp range',
        q ='Toronto',
        q_axis='y',
        whisker_caps=True,
        outlier_marker='diamond',
        outlier_kwargs=dict(size=10, color=tableau_colors[3]),
        box_kwargs=dict(fill_color=tableau_colors[2], width=.75),
        whisker_kwargs=dict(line_color='#7C0000', line_width=3),
        toolbar_location = 'right',
        tools=tools,
        title="Tor. electricity demand by outdoor temperature, 2002"+endash+"2015"
        )

        p3_box.yaxis.axis_label = 'MW'
        #grid = gridplot([p1_box, p2_box, p3_box], ncols=2, width=250, height=250)
        st.bokeh_chart(p2_box)
        with st.expander('see boxcharts for day of week and outdoor temperature'):
            st.bokeh_chart(p1_box)
            st.bokeh_chart(p3_box)

    with col2:
        st.markdown('### EV charging and electric heat')
        ev_heat_blurb = '''
Transport and heating are Ontario&#8217;s largest energy categories, by far. When these major categories of energy use are electrified, what will their demands look like? Certainly outdoor temperature in a northern city like Toronto with cold winters will strongly influence the level of Toronto electrical demand. Cold temperatures can cut EV range in half, because of cabin heat demand. This will increase frequency of EV charging, and could have a dramatic impact on system peak demand.

The box plot showing Toronto demand in various outdoor temperature conditions shows dramatic demand increases when outdoor temperature exceeds 29°C. But ***energy*** demand is much greater when outdoor temperature falls below minus 10°C. That ***energy*** demand is for heating, and today it is met mostly by natural gas, a fossil fuel we are trying to phase out. If and when that energy demand is met with electricity, Toronto electricity demand will change dramatically.
        '''
        st.markdown(ev_heat_blurb)

        st.image(full_path+'feature_importances.jpg')
    with col1:
        st.markdown('### More variable renewables, plus electrification, means &#8220;balancing&#8221; supply works harder and less efficiently. This increases system costs')
        st.markdown('Grid operators in systems with high VRE penetration match supply with **net demand** which is demand minus wind and solar. Wind output is a random variable that ranges from zero to close to maximum capacity, with output more likely at the lower end. Solar output is certain to be zero at night. This means that grid operators rely on a sub-fleet of supply sources capable of fast collective response to both demand and wind conditions.')
    with col2:
        st.markdown('### Electrification example: Metrolinx electrified trains will introduce major changes in current demand patterns, especially in winter')
        st.markdown('The energies involved in replacing diesel power with electric power in the Metrolinx system will heighten the entire provincial demand curve, sharpen the peaks, and introduce great variability from day to day. Winter heating demand will shift demands ever higher (remember that the GO system, unlike the Toronto subway, is almost entirely outdoors.')
