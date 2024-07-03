import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load data
file_path = '/content/LRI_short.dta'
data = pd.read_stata(file_path)

# Initialize the Dash app
app = Dash(__name__)
server=app.server

# List of indicators for the dropdown
indicators = ['lri', 'employment_forms', 'working_time', 'dismissal',
              'employee_representation', 'industrial_action']

# List of years for the dropdown
years = data['year'].unique()

# Layout of the app
app.layout = html.Div([
    html.H1("Interactive Dashboard"),
    html.P("This dashboard allows you to explore various labor market indicators across different countries and years. Select an indicator and year to see the data visualized on the map."),
    html.Div([
        dcc.Dropdown(
            id='indicator-dropdown',
            options=[{'label': indicator.replace('_', ' ').title(), 'value': indicator} for indicator in indicators],
            value='lri',  # Default value
            style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'middle', 'margin-right': '1%'}
        ),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': str(year), 'value': year} for year in years],
            value=years[0],  # Default value
            style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'middle'}
        ),
    ], style={'textAlign': 'center'}),
    dcc.Graph(id='choropleth-map'),
    html.Button("Download Entire Dataset", id="btn-download-entire", style={'margin-top': '10px'}),
    dcc.Download(id="download-entire-dataframe-csv"),
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': country, 'value': country} for country in data['country'].unique()],
        value=data['country'].unique()[0],  # Default value
        style={'margin-top': '20px'}
    ),
    dcc.Graph(id='lri-graph'),
    dcc.Graph(id='employment-forms-graph'),
    dcc.Graph(id='working-time-graph'),
    dcc.Graph(id='dismissal-graph'),
    dcc.Graph(id='employee-representation-graph'),
    dcc.Graph(id='industrial-action-graph'),
    html.Button("Download Filtered Data", id="btn-download"),
    dcc.Download(id="download-dataframe-csv")
])

# Define callback functions to update the graphs and handle data download
@app.callback(
    [
        Output('choropleth-map', 'figure'),
        Output('lri-graph', 'figure'),
        Output('employment-forms-graph', 'figure'),
        Output('working-time-graph', 'figure'),
        Output('dismissal-graph', 'figure'),
        Output('employee-representation-graph', 'figure'),
        Output('industrial-action-graph', 'figure')
    ],
    [
        Input('indicator-dropdown', 'value'),
        Input('year-dropdown', 'value'),
        Input('country-dropdown', 'value')
    ]
)
def update_graphs(selected_indicator, selected_year, selected_country):
    filtered_data = data[data['country'] == selected_country]
    year_data = data[data['year'] == selected_year]

    # Create time series graphs for each indicator
    lri_fig = px.line(filtered_data, x='year', y='lri', title='LRI Over Time')
    employment_forms_fig = px.line(filtered_data, x='year', y='employment_forms', title='Employment Forms Over Time')
    working_time_fig = px.line(filtered_data, x='year', y='working_time', title='Working Time Over Time')
    dismissal_fig = px.line(filtered_data, x='year', y='dismissal', title='Dismissal Over Time')
    employee_representation_fig = px.line(filtered_data, x='year', y='employee_representation', title='Employee Representation Over Time')
    industrial_action_fig = px.line(filtered_data, x='year', y='industrial_action', title='Industrial Action Over Time')

    # Create choropleth map for the selected indicator and year
    choropleth_fig = px.choropleth(
        year_data,
        locations="country",
        locationmode="country names",
        color=selected_indicator,
        hover_name="country",
        title=f'{selected_indicator.replace("_", " ").title()} in {selected_year}'
    )

    choropleth_fig.update_layout(
        coloraxis_colorbar=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.25,
            xanchor='center',
            x=0.5,
            title=None
        )
    )

    return (choropleth_fig, lri_fig, employment_forms_fig, working_time_fig, dismissal_fig, employee_representation_fig, industrial_action_fig)

@app.callback(
    Output('download-dataframe-csv', 'data'),
    [Input('btn-download', 'n_clicks')],
    [Input('country-dropdown', 'value')],
    prevent_initial_call=True
)
def download_filtered_data(n_clicks, selected_country):
    filtered_data = data[data['country'] == selected_country]
    return dcc.send_data_frame(filtered_data.to_csv, "filtered_data.csv")

@app.callback(
    Output('download-entire-dataframe-csv', 'data'),
    [Input('btn-download-entire', 'n_clicks')],
    prevent_initial_call=True
)
def download_entire_data(n_clicks):
    return dcc.send_data_frame(data.to_csv, "entire_data.csv")

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
