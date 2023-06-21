import dash
from dash import html, dcc, Input, Output, dash_table
import plotly.graph_objs as go
import numpy as np
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
import pandas as pd


app = dash.Dash()
server = app.server

load_dotenv(dotenv_path='.env')

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
SQL_ALCHEMY_CONN_STRING = os.getenv('SQL_ALCHEMY_CONN_STRING')


def get_sql_alchemy_engine(conn_string) -> Connection:
    """Gets an SQL Alchemy engine connection object

    Args:
        conn_string (string): a connection string to connect to PostgreSQL database

    Returns:
        Connection: A connection object using SqlAlchemy
    """
    db = create_engine(conn_string)
    conn = db.connect()
    conn.autocommit = True
    
    return conn


conn = get_sql_alchemy_engine(SQL_ALCHEMY_CONN_STRING)
df = pd.read_sql_query('SELECT * FROM listing', conn)
list_of_provinces = df['province'].unique().tolist()

# print(data.head())
def days_on_market():
    rental_listing_by_province = df.groupby(['province'])['mls_num'].count().reset_index(name= 'num_of_listing')
    # trace = [go.Bar(x=rental_listing_by_province['province'], y=rental_listing_by_province['num_of_listing'], marker={'color': rental_listing_by_province['num_of_listing']})]
    
    trace = [go.Pie(labels=rental_listing_by_province['province'], values=rental_listing_by_province['num_of_listing'],
                textinfo='label+percent',
                insidetextorientation='radial',
                pull=[0, 0, 0, 0.3])]
    return dict(data=trace, layout=go.Layout(title='Number of Rental Listings per Province'))



@app.callback(Output(component_id='table', component_property='data'),
                [Input(component_id='dropdownio', component_property='value')])
def get_table_data(province):
    dff = df[df['province'] == province]
    return dff.to_dict('records')
    
    
    

@app.callback(
    Output(component_id='my-div', component_property='figure'),
    [Input(component_id='dropdownio', component_property='value')])
def update_output_div(input_value):
    
    filtered_df_by_province = df[(df['province'] == input_value) & (df['property_type'] == 'Single Family')]
    avg_price_by_city = filtered_df_by_province.groupby(['city'])['price'].mean().round(0).reset_index(name='average_price')
    # print(avg_price_by_city.head())
    trace = [go.Bar(x=avg_price_by_city['city'], y=avg_price_by_city['average_price'], name='Average price by city')]
    return dict(data=trace, layout=go.Layout(title='Average Price per City'))



app.layout = html.Div(children=[
    html.Div(id='graphs-container',children=[
        html.Div(id='sub-container',children=[
            dcc.Dropdown(id='dropdownio',
            options=[
                {'label': province, 'value': province} for province in list_of_provinces
            ], value='NL'),
        
            dcc.Graph(id='my-div')]),
        
        dcc.Graph(figure=days_on_market(), id='on-market')
        
        ]),
    html.Div(id='table-container', children=[
            dash_table.DataTable(
            id='table',
            # columns=[{'name': i, 'id': i} for i in df.columns],
            # data=df.to_dict('records'),
            style_cell={'textAlign': 'left', 'whiteSpace': 'normal', 'height': 'auto'},
            style_header={'backgroundColor': 'lavender', 'fontWeight': 'bold'},
            page_size=10
        )
    ])
    # dcc.Graph(figure=get_table_data(), id='table-data')
    
], id='container')



if __name__ == '__main__':
    server.run()