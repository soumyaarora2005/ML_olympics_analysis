import numpy as np
import streamlit as st
import pandas as pd

@st.cache_data
def fetch_medal_tally(df, year, country):
    medal_df = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    flag = 0
    if year == 'Overall' and country == 'Overall':
        temp_df = medal_df
    if year == 'Overall' and country != 'Overall':
        flag = 1
        temp_df = medal_df[medal_df['region'] == country]
    if year != 'Overall' and country == 'Overall':
        temp_df = medal_df[medal_df['Year'] == int(year)]
    if year != 'Overall' and country != 'Overall':
        temp_df = medal_df[(medal_df['Year'] == year) & (medal_df['region'] == country)]

    if flag == 1:
        x = temp_df.groupby('Year').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Year').reset_index()
    else:
        x = temp_df.groupby('region').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Gold',
                                                                                      ascending=False).reset_index()

    x['total'] = x['Gold'] + x['Silver'] + x['Bronze']

    x['Gold'] = x['Gold'].astype('int')
    x['Silver'] = x['Silver'].astype('int')
    x['Bronze'] = x['Bronze'].astype('int')
    x['total'] = x['total'].astype('int')

    return x

@st.cache_data
def country_year_list(df):
    years = df['Year'].unique().tolist()
    years.sort()
    years.insert(0, 'Overall')

    country = np.unique(df['region'].dropna().values).tolist()
    country.sort()
    country.insert(0, 'Overall')

    return years,country

@st.cache_data
def data_over_time(df,col):

    nations_over_time = df.drop_duplicates(['Year', col])['Year'].value_counts().reset_index().sort_values('Year')
    nations_over_time.rename(columns={'Year': 'Edition', 'count': col}, inplace=True)
    return nations_over_time

@st.cache_data
def most_successful(df, sport):
    temp_df = df.dropna(subset=['Medal'])

    if sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]

    # Get medal counts per athlete
    medal_counts = temp_df['Name'].value_counts().reset_index()
    medal_counts.columns = ['Name', 'Medals']
    
    # Get top 15 athletes
    top_athletes = medal_counts.head(15)
    
    # Merge with original dataframe
    merged = top_athletes.merge(df, on='Name', how='left', suffixes=('', '_y'))
    
    # Reset index to have it as a column
    merged = merged.reset_index()
    
    # Select the required columns
    # 'index' from reset_index, 'Name' (which is the original name), 'Sport', 'region'
    x = merged[['index', 'Name', 'Sport', 'region']].drop_duplicates('Name')
    
    # Rename columns as per your original intention
    x.rename(columns={'index': 'Name', 'Name': 'Medals'}, inplace=True)
    
    return x
# def most_successful(df, sport):
    temp_df = df.dropna(subset=['Medal'])

    if sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]

    x = temp_df['Name'].value_counts().reset_index()
    x.columns=['Name','Medals']
    x=x.head(15).merge(df,on='Name', how='left')
    x=x[['index', 'Name_x', 'Sport', 'region']].drop_duplicates('Name')
    x.rename(columns={'index': 'Name', 'Name_x': 'Medals'}, inplace=True)
    return x

@st.cache_data
def yearwise_medal_tally(df,country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'], inplace=True)

    new_df = temp_df[temp_df['region'] == country]
    final_df = new_df.groupby('Year').count()['Medal'].reset_index()

    return final_df

@st.cache_data
def country_event_heatmap(df,country):
    temp_df = df.dropna(subset=['Medal'])
    if temp_df.empty:
        return pd.DataFrame()
    temp_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'], inplace=True)

    new_df = temp_df[temp_df['region'] == country]

    if new_df.empty:
        print("No medal data found for {country}")
        return pd.DataFrame()

    pt = new_df.pivot_table(index='Sport', columns='Year', values='Medal', aggfunc='count').fillna(0)

    if not pt.empty:
        pt['Total'] = pt.sum(axis=1)
        pt = pt.sort_values('Total', ascending=False)
        pt = pt.drop('Total', axis=1)
    return pt

@st.cache_data
def most_successful_countrywise(df, country):
    temp_df = df.dropna(subset=['Medal'])

    temp_df = temp_df[temp_df['region'] == country]

    if temp_df.empty:
        return pd.DataFrame()

    x = temp_df['Name'].value_counts().reset_index()
    x.columns=['Name','Medals']
    x=x.head(10)
    merged = x.merge(df, on='Name', how='left')
    x=merged[['Name', 'Medals', 'Sport']].drop_duplicates('Name')
    
    return x

@st.cache_data
def weight_v_height(df,sport):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    athlete_df['Medal']=athlete_df['Medal'].fillna('No Medal')
    if sport != 'Overall':
        temp_df = athlete_df[athlete_df['Sport'] == sport]
    else:
        temp_df= athlete_df
    temp_df = temp_df.dropna(subset=['Height', 'Weight'])
    
    return temp_df

#@st.cache_data
def men_vs_women(df, sport='Overall'):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    # Filter by sport if not 'Overall'
    if sport != 'Overall':
        athlete_df = athlete_df[athlete_df['Sport'] == sport]
    
    # Check if data exists after filtering
    if athlete_df.empty:
        return pd.DataFrame(columns=['Year', 'Male', 'Female'])

    men = athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index(name='Male')
    women = athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index(name='Female')

    final = men.merge(women, on='Year', how='outer')
#final.rename(columns={'Name_x': 'Male', 'Name_y': 'Female'}, inplace=True)

    final.fillna(0, inplace=True)
    final = final.sort_values('Year')

    return final

