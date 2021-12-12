import pandas as pd
import warnings
import streamlit as st

class data_analysis:
    def __init__(self,
                 data=None,
                 extn=None,
                 name=None):
        if data is None:
            warnings.warn('No data has been passed to the class object')
        else:
            self.orig_data = data.copy()
            self.data = data.copy()
            self.extn = extn
            self.name = name
            self.get_sample_size()
            self.column_summary()

    def get_sample_size(self):
        self.head_length=25
        if len(self.data)<25:
            self.head_length=len(self.data)
        self.size_info=pd.DataFrame({'File Name':[self.name],
                                     'File Type':[self.extn],
                                     'Table Size':[str(self.data.shape[0])+" x "+str(self.data.shape[-1])]})

    def column_summary(self):
        self.col_sum = pd.DataFrame(self.data.dtypes,
                                        columns=['Datatype'])

        self.col_sum['Count'] = self.data.count()
        self.col_sum['Unique Values'] = self.data.nunique()
        self.col_sum['Missing Values'] = self.data.isnull().sum()
        self.col_sum['Cardinality Score'] = (self.data.nunique()*100/(len(self.data) - self.col_sum['Missing Values'])).round(2)
        self.col_sum = self.col_sum.reset_index()
        self.col_sum['Possible Datetime column'] = self.col_sum['index'].apply(lambda x: "Yes" if 'date' in x.lower()\
                                                                                     else "Yes" if 'time' in x.lower()\
                                                                                     else " ")
        self.col_sum = self.col_sum.set_index("index")
        self.vdistinct_cols = [col for col in self.data.columns if (self.data[col].nunique()<=5) and (self.data[col].dtypes=='O')]

    def return_col_summary(self,col,type):
        ind_sum = {}
        ind_sum['Type'] = type
        ind_sum['Total Values'] = len(self.data[col].dropna())
        ind_sum['Distinct Values'] = self.data[col].nunique()
        ind_sum['Missing Values'] = len(self.data)-len(self.data[col].dropna())
        if ind_sum['Distinct Values']/ind_sum['Total Values']>0.85:
            ind_sum['Cardinality'] = "Very High"
        elif ind_sum['Distinct Values']/ind_sum['Total Values']>0.60:
            ind_sum['Cardinality'] = "High"
        elif ind_sum['Distinct Values']/ind_sum['Total Values']>0.35:
            ind_sum['Cardinality'] = "Low"
        else:
            ind_sum['Cardinality'] = "Very Low"
        ind_sum['Distinct %'] = str(round(ind_sum['Distinct Values']*100/ind_sum['Total Values'],2))+" %"

        if type in ['int64','int32','float64','float32','int','float']:
            ind_sum['Minimum'] = round(float(self.data[col].min()),2)
            ind_sum['Maximum'] = round(float(self.data[col].max()),2)
            ind_sum['Mean'] = round(float(self.data[col].mean()),2)
            ind_sum['25%'] = round(float(self.data[col].quantile(0.25)), 2)
            ind_sum['50%'] = round(float(self.data[col].quantile(0.50)), 2)
            ind_sum['75%'] = round(float(self.data[col].quantile(0.75)), 2)
            ind_sum['Skew'] = round(float(self.data[col].skew()), 2)

        elif type=='O':
            most_occurring = round(self.data[col].value_counts()[0] * 100 / ind_sum['Total Values'],2)
            least_occurring = round(self.data[col].value_counts()[-1] * 100 / ind_sum['Total Values'],2)

            ind_sum['Most Occurring Value'] = str(self.data[col].value_counts().index[0]) + f" ({most_occurring} %)"
            ind_sum['Least Occurring Value'] = str(self.data[col].value_counts().index[-1]) + f" ({least_occurring} %)"
        ind_sum['Memory Usage'] = str(round(self.data[col].memory_usage() * 1e-6, 2)) + " MB"
        return ind_sum

    def col_headlength(self,col,limit):
        self.col_length = int(self.data[col].nunique())
        self.flag_1=1
        if self.col_length > limit:
            self.col_length = limit
            self.flag_1 = 0
        return self.col_length

    def return_catcol_summary(self,col):
        col_length = self.col_headlength(col,8) # top 8 values at max
        if col_length<8:
            self.vals = self.data[col].value_counts()
        else:
            self.vals = self.data[col].value_counts().head(col_length)

        if self.flag_1==0:
            self.vals = self.vals.append(pd.Series([self.data[col].value_counts().iloc[col_length:].sum()],index=['Others']))
        self.vals_df = pd.DataFrame(self.vals,columns=['Frequency'])
        self.vals_df['%'] = ((self.vals_df['Frequency'] * 100/ self.return_col_summary(col,"O")['Total Values']).round(2)).astype(str) + " %"
        return self.vals_df

    def return_missing_data(self):
        self.miss = self.data.isnull()
        self.miss_summary = pd.DataFrame(self.miss.sum()).reset_index()
        self.miss_summary.columns=['Column Name','Missing Rows']
        self.miss_summary['Within Column %'] = ((self.miss_summary['Missing Rows']*100/len(self.data)).round(2)).astype(str) + " %"
        self.miss_summary['Overall Contribution %'] = ((self.miss_summary['Missing Rows']*100 / self.miss_summary['Missing Rows'].sum()).round(2)).astype(str) + " %"
        self.miss_label=self.miss.replace({True:"Missing",False:"Not Missing"})
        return self.miss_summary



