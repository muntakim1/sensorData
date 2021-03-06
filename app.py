import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_daq as daq
import dash
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import math
import plotly.express as px
import time
#initialize the app
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

# adding title
app.title="IoT Monitoring"

# Loading Data Set to the pandas
df = pd.read_csv('iot_telemetry_data.csv')

# Get Data slice function
def flow_from_df(dataframe: pd.DataFrame, chunk_size: int = 15):
    for start_row in range(0, dataframe.shape[0], chunk_size):
        end_row = min(start_row + chunk_size, dataframe.shape[0])
        yield dataframe.iloc[start_row:end_row, :]

# Sidebar styles
        
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "backgroundColor": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "marginLeft": "18rem",
    "marginRight": "2rem",
    "padding": "2rem 1rem",
    "justifyContent":"center",
    
}

# SideBar 
sidebar = html.Div(
    
    [
        html.H2(children=["Top",html.Span("Value",style={'color':"#7b2cBd"})], className="display-4"),
        html.Hr(),
        html.P(
            "Real Time IoT device data monitor", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Predictions", href="/predictions", active="exact"),
                dbc.NavLink("Big Query Actions", href="/bigquery", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

# Navbar 
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home",  active="exact", href="/")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("About Us", href="#"),
                dbc.DropdownMenuItem("Contact Us", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="IoT Data Monitoring System (RealTime)",
    brand_href="#",
    color="dark",
    dark=True,
)
# Content 
content=html.Div(
            id="content",
   
            style=CONTENT_STYLE
        )


# Main App layout 
app.layout = html.Div(
    # style={"backgroundColor": "#212121","color":"white"},
    children=[
        dcc.Location(id="url"),
        navbar,
        sidebar,
        content,
        ]
)


# Callback for Routing 

@app.callback(Output("content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname =="/":
        mainPageContent = [

            html.Div(id="figures"),
            dcc.Interval(
                id='interval-component',
                interval=3*1000,  # in milliseconds
                n_intervals=0
            ),
            ]

        return mainPageContent
    elif pathname == "/predictions":
        return html.P("Content of the page is in Under Development ",className="text-danger")
    elif pathname == "/bigquery":
        return html.P("Content of the page is in Under Development with Google's Big Quey and Table ",className="text-danger")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

# Call back for Figure live update 
@app.callback(Output('figures', 'children'),
              Input('interval-component', 'n_intervals'))
def UpdataPage(n_intervals):
    get_chunk = flow_from_df(df)
    for x in range(n_intervals):
        data = next(get_chunk)

    data.ts=pd.to_datetime(data['ts'],unit='ms')
    fig = make_subplots(rows=3, cols=2,horizontal_spacing=0.05, vertical_spacing=0.1,subplot_titles=("time vs CO","time vs humidity", "time vs temperature","time vs lpg","time vs Smoke"))
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 30
    }


    fig.append_trace({
        'x': data['ts'],
        'y': data['co'],
        'name': 'Time vs CO',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 1, 1)
    fig.append_trace({
        'x': data['ts'],
        'y': data['humidity'],
        'text': data['humidity'],
        'name': 'time vs humidity',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 2, 1)
    fig.append_trace({
        'x': data['ts'],
        'y': data['temp'],
        'text': data['humidity'],
        'name': 'time vs temperature',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 1, 2)
    fig.append_trace({
        'x': data['ts'],
        'y': data['lpg'],
        'text': data['lpg'],
        'name': 'time vs lpg',
        'mode': 'lines',
        'type': 'scatter'
    }, 2, 2)

    fig.append_trace({
        'x': data['ts'],
        'y': data['smoke'],
        'text': data['smoke'],
        'name': 'time vs smoke',
        'mode': 'lines',
        'type': 'scatter'
    }, 3, 1)
    fig.update_layout(height=700, showlegend=False)


  

    Tanker = daq.Gauge(
        
        value=data['lpg'].mean()*100,
        label='LPG in PPM',
        max=1,
        min=0,
        color={"gradient": True, "ranges": {
            "green": [0, .6], "yellow": [.6, .8], "red": [.8, 1]}},
    )

    Smoke = daq.Gauge(

        value=data['smoke'].mean()*100,
        label='Smoke in PPM',
        max=2.5,
        min=0,
        color={"gradient": True, "ranges": {
            "green": [0, 1.5], "yellow": [1.5, 2], "red": [2, 2.5]}},
    )
    Co = daq.Gauge(

        value=data['co'].mean()*100,
        label='CO in PPM',
        max=1,
        min=0,
        color={"gradient": True, "ranges": {
            "green": [0, .6], "yellow": [.6, .8], "red": [.8, 1]}},
    )

    Temp = daq.Thermometer(
        id='my-daq-thermometer',
        min=math.floor(data['temp'].min()),
        max=math.floor(data['temp'].max()),
        value=data['temp'].mean(),
        label="Temperature (F)",
        color="#9B51E0",
        
    )

    motion = daq.Indicator(
        id='my-daq-indicator',
        value=data['light'][:1].values[0],
        label="Light Status",
        color='#b71c1c',
        style={
            'color': '#black'
        }
    )

   
    hour = time.localtime(time.time())[3]
    hour = str(hour).zfill(2)

    minute = time.localtime(time.time())[4]
    minute = str(minute).zfill(2)
    Watch = daq.LEDDisplay(
            id='control-panel-utc-component',
            value=hour+':'+minute,
            label='Watch',
            size=50,
        color='#4a148c',
        )
    Row=dbc.Row(
        children=[
            dbc.Col(
                children=[motion, html.Br(),Watch]
            ),
            dbc.Col(
                children=[ Temp]
            ),
            dbc.Col(
                children=[Tanker]
            ),
           
            dbc.Col(
                children=[Smoke]
            ),
            dbc.Col(
                children=[Co]
            )
        ]
        )

    charts = dcc.Graph(figure=fig, config={"displayModeBar": False})
    return [Row, charts]



server = app.server

# if __name__=="__main__":
#     app.run_server(debug=True)
