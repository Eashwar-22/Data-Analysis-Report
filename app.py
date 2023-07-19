import streamlit as st
import pandas as pd
from report_class import data_analysis
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(layout="wide",
                   page_title="Data Analysis App",
                   page_icon="‍🗞")

def header(url):
    st.markdown(f'<p style="color:#186e5f;font-size:30px;font-weight:bold;font-family: 	Palatino;'
                f'border-radius:2%;">{url}</p>',
                unsafe_allow_html=True)
def subheader(url):
    st.markdown(f'<p style="color:#3d8f81;font-size:25px;font-weight:bold;font-family: 	Palatino;'
                f'border-radius:2%;">{url}</p>',
                unsafe_allow_html=True)
def lilheader(url,col):
    col.markdown(f'<p style="color:#60a398;font-size:20px;font-weight:bold;font-family: 	Palatino;'
                f'border-radius:2%;">{url}</p>',
                unsafe_allow_html=True)
def color_red_green(val):
    if float(val) > 50:
        color = 'green'
    elif float(val)>20:
        color='orange'
    else:
        color='red'
    return f'color: {color}'
def color_red(val):
    if int(val) == 1:
        color = 'red'
    else:
        color = 'black'
    return f'color: {color}'
def plot_distribution(i,marginal,category=None):
    if category is not None:
        df = obj.data[[i,category]].dropna()
        cat_order = {category: sorted(list(df[category].unique()))}
    else:
        df = obj.data[i].dropna()
        cat_order = None

    fig = px.histogram(df,
                       x=i,
                       marginal=marginal,
                       color=category,
                       category_orders=cat_order,
                       title=f"Distribution of {i}",
                       opacity=0.8,
                       width=1200, height=600)
    st.plotly_chart(fig)

header("What's the Story?")

det = st.expander("Expand for details")
with det:
    st.markdown('''
    * Upload an Excel/CSV file and click on Analyse to produce results.
    * For ease of compatibility and conciseness it is recommended to upload a file with 10 columns max. 
    * If no file is uploaded, a sample file vgsales.csv is used by default.
    * Source Code : https://github.com/Eashwar-22/Data-Analysis-Report
    ''')
st.markdown(" --- ")

with st.sidebar:
    uploaded_file = st.file_uploader("Upload an Excel/CSV file (upto 10 columns recommended")
    additional = st.expander("Advanced")
    delim=","
    with additional:
        delim = st.text_input("Enter Delimiter for csv file : ",value=",")
    press = st.checkbox("Analyse")
    feature = st.radio("Features",['Overview','Column Information','Missing Data','Actions'])


sample_file='vgsales.csv'
extn='CSV'
df = pd.read_csv(sample_file)
obj = data_analysis(data = df,
                    extn = extn,
                    name = sample_file)

if uploaded_file is not None and press==True:
    if uploaded_file.name.split('.')[-1] in ['xlsx','xls']:
        extn='Excel'
        df = pd.read_excel(uploaded_file)
    elif uploaded_file.name.split('.')[-1]=='csv':
        extn='CSV'
        df = pd.read_csv(uploaded_file,delimiter=delim)

    obj = data_analysis(data = df,
                        extn = extn,
                        name = uploaded_file.name)


if feature == 'Overview':
    st.table(obj.size_info.assign(hack='').set_index('hack').T)
    st.markdown(" --- ")
    subheader("Sample Data")
    lilheader(f"First {obj.head_length} rows",st)

    fig1 = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df[col].head(obj.head_length) for col in df.columns],
                   fill_color='#d5ded6',
                   align='left'))
    ])
    fig2 = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df[col].tail(obj.head_length) for col in df.columns],
                   fill_color='#d5ded6',
                   align='left'))
    ])


    for f in [fig1,fig2]:
        f.update_layout(
            width=1400,
            height=600,
            margin={'l':0,'t':0,'b':0})
    st.plotly_chart(fig1)
    lilheader(f"Last {obj.head_length} rows", st)
    st.plotly_chart(fig2)
    st.markdown(" --- ")
    subheader("Column Info")



    st.dataframe(obj.col_sum.astype(str).style.applymap(color_red_green, subset=['Cardinality Score']).applymap(color_red, subset=['Unique Values']),
                 height=55*len(df.columns)
            )
    st.markdown(" --- ")
    subheader("Numerical Column Description")
    st.dataframe(obj.data.describe().astype(int))


if feature == 'Column Information':
    subheader("Column Info")


    st.dataframe(obj.col_sum.astype(str).style.applymap(color_red_green, subset=['Cardinality Score']).applymap(color_red, subset=['Unique Values']),
                 height=55*len(obj.data.columns)
            )
    st.markdown(" --- ")
    expand_all_cols = st.sidebar.checkbox("Check to expand all information (dont click if the file contains more than 35 columns!)", key="expand_all_cols")

    for i in obj.col_sum.index:
        col1,col2,col3=st.columns(3)

        type = obj.col_sum.loc[i, 'Datatype']
        c = obj.return_col_summary(i,type)

        col_summary = pd.DataFrame({i:[j] for i,j in c.items()})

        lilheader(i,col1)
        col2.write(col_summary.astype(str).assign(hack='').set_index('hack').T)
        if type in ['int64','int32','float64','float32','int','float']:
            plot_dist = st.expander(f"View Distribution of {i}")
            if expand_all_cols:
                plot_dist=None
                marginal = st.radio("Select Distribution", ['box','violin','rug'],key=i + "_margdist_plot1")
                category = st.selectbox("Select Category", [None]+obj.vdistinct_cols, key=i + "_category_1")
                plot_distribution(i, marginal, category)
            else:
                with plot_dist:
                    marginal = st.radio("Select Distribution", ['box', 'violin', 'rug'], key=i + "_margdist_plot2")
                    category = st.selectbox("Select Category", [None]+obj.vdistinct_cols, key=i + "_category_2")
                    plot_distribution(i, marginal, category)
        elif type=='O':
            plot_cat_stat = st.expander(f"View Category Stats of {i}")
            if expand_all_cols:
                lilheader(f"Frequency of Top {obj.col_headlength(i,8)} Occurring Values",st)
                st.write(obj.return_catcol_summary(i))
            else:
                with plot_cat_stat:
                    lilheader(f"Frequency of Top {obj.col_headlength(i,8)} Occurring Values", st)
                    st.write(obj.return_catcol_summary(i))


        st.markdown("---")

if feature=='Missing Data':
    miss_summary = obj.return_missing_data()
    subheader(" Missing Data Summary")
    lilheader(f" Table Length : {len(obj.data)}",st)
    st.dataframe(miss_summary.assign(hack='').set_index('hack'),
             height=55*len(obj.data.columns))
    st.markdown("---")
    subheader(f" Bar Plot for Missing Data")
    fig = px.bar(miss_summary, x='Column Name', y='Missing Rows')
    fig.update_layout(
        width=1000,
        height=400,
        margin={'l': 0, 't': 0, 'b': 0})
    st.plotly_chart(fig)
    st.markdown("---")
    subheader(f" Distribution of Missing Data")
    fig = px.imshow(obj.miss)
    st.plotly_chart(fig)
    st.markdown("---")
    subheader(f" Column Comparison of Missing Data")
    x = st.selectbox("Choose X Axis : ",obj.data.columns)
    y = st.selectbox("Choose Y Axis : ", obj.data.columns)
    fig = px.density_heatmap(obj.miss_label, x=x, y=y)
    st.plotly_chart(fig)
    st.markdown("---")
    subheader(f" Correlation of Occurrence of Missing Data")
    fig = px.imshow(obj.miss.corr().replace({True:1,False:0}))
    st.plotly_chart(fig)






if feature=='Actions':
    p=st.multiselect('Convert to Datetime', list(obj.data.columns))
    st.write(p)
    subheader("( WIP )")




