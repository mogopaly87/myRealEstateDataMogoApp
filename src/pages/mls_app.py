import dash
from dash import html, dcc, Input, Output, dash_table, callback
import plotly.graph_objs as go
import numpy as np
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
import pandas as pd


# from server import app
# app = dash.Dash(__name__, url_base_pathname='/dashapp/')
dash.register_page(__name__, path='/mls')
# server = app.server

load_dotenv(dotenv_path='/home/nonso/Desktop/playground/plotlydash/src/.env')

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
SQL_ALCHEMY_CONN_STRING = os.getenv('SQL_ALCHEMY_CONN_STRING')

print(f">>>>>>>>>>>>>>>>>>>>\n ALCHEMY STRING IS: {SQL_ALCHEMY_CONN_STRING}\n")
def get_sql_alchemy_engine(conn_string) -> Connection:
    """Gets an SQL Alchemy engine connection object

    Args:
        conn_string (string): a connection string to connect to PostgreSQL database

    Returns:
        Connection: A connection object using SqlAlchemy
    """
    db = create_engine(conn_string, pool_size=20, max_overflow=0)
    conn = db.connect()
    conn.autocommit = True
    
    return conn


conn = get_sql_alchemy_engine(SQL_ALCHEMY_CONN_STRING)
df = pd.read_sql_query('SELECT * FROM listing', conn)
list_of_cities = df['city'].unique().tolist()

# print(data.head())
def days_on_market():
    rental_listing_by_cities = df.groupby(['city'])['mls_num'].count().reset_index(name= 'num_of_listing')
    # trace = [go.Bar(x=rental_listing_by_province['province'], y=rental_listing_by_province['num_of_listing'], marker={'color': rental_listing_by_province['num_of_listing']})]
    
    trace = [go.Pie(labels=rental_listing_by_cities['city'], values=rental_listing_by_cities['num_of_listing'],
                textinfo='label+percent',
                insidetextorientation='radial',
                pull=[0, 0, 0, 0.3])]
    return dict(data=trace, layout=go.Layout(title='Percentage Inventory by City'))



@callback(Output(component_id='table', component_property='data'),
                [Input(component_id='dropdownio', component_property='value')])
def get_table_data(city):
    dff = df[df['city'] == city]
    return dff.to_dict('records')
    
    
    

@callback(
    Output(component_id='my-div', component_property='figure'),
    [Input(component_id='dropdownio', component_property='value')])
def update_output_div(input_value):
    
    filtered_df_by_city= df[(df['city'] == input_value) & (df['property_type'] == 'Single Family')]
    avg_price_by_city = filtered_df_by_city.groupby(['city'])['price'].mean().round(0).reset_index(name='average_price')
    # print(avg_price_by_city.head())
    trace = [go.Bar(x=avg_price_by_city['city'], y=avg_price_by_city['average_price'], name='Average price by city')]
    return dict(data=trace, layout=go.Layout(title='Average Price per City'))




layout = html.Div(children=[
    html.Div(id='graphs-container',children=[
        html.Div(id='sub-container',children=[
            dcc.Dropdown(id='dropdownio',
            options=[
                {'label': city, 'value': city} for city in list_of_cities
            ], value='St. John\'s'),
        
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




# if __name__ == '__main__':
#     server.run(port='5000')