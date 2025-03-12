import base64
import io
import dash
from dash import dash_table  # New import for data table
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
import pandas as pd
import plotly.express as px

app = dash.Dash(__name__)
app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div(['Drag and Drop or ', html.A('Select CSV File')]),
        style={
            'width': '100%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
            'textAlign': 'center', 'margin': '10px'
        },
        multiple=False
    ),
    
    # New data preview table
    dash_table.DataTable(
        id='data-preview',
        style_table={'overflowX': 'auto', 'margin': '10px', 'maxWidth': '95%'},
        style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'},
        page_size=7
    ),
    
    html.Div([
        dcc.Dropdown(id='column-selector', placeholder='Select Column'),
        dcc.Dropdown(
            id='plot-type-selector',
            options=[
                {'label': 'Histogram', 'value': 'histogram'},
                {'label': 'Scatter Plot', 'value': 'scatter'},
                {'label': 'Bar Chart', 'value': 'bar'},
                {'label': 'Pie Chart', 'value': 'pie'},
                {'label': 'Line Chart', 'value': 'line'}
            ],
            placeholder='Select Plot Type'
        )
    ], style={'padding': '20px'}),
    
    dcc.Store(id='stored-data'),
    dcc.Graph(id='output-graph')
])

def parse_contents(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return pd.read_csv(io.StringIO(decoded.decode('utf-8')))

# New callback for data preview
@app.callback(
    [Output('data-preview', 'data'),
     Output('data-preview', 'columns')],
    Input('upload-data', 'contents')
)
def update_preview(contents):
    if not contents:
        return [], []
    
    df = parse_contents(contents)
    columns = [{'name': col, 'id': col} for col in df.columns]
    return df.head(10).to_dict('records'), columns

# Existing callbacks remain the same
@app.callback(
    Output('stored-data', 'data'),
    Input('upload-data', 'contents')
)
def store_data(contents):
    if contents:
        return parse_contents(contents).to_dict('records')
    return None

@app.callback(
    Output('column-selector', 'options'),
    Input('stored-data', 'data')
)
def update_columns(data):
    if data:
        df = pd.DataFrame(data)
        return [{'label': col, 'value': col} for col in df.columns]
    return []

@app.callback(
    Output('output-graph', 'figure'),
    [Input('column-selector', 'value'),
     Input('plot-type-selector', 'value'),
     Input('stored-data', 'data')]
)
def update_graph(selected_column, plot_type, data):
    if not all([selected_column, plot_type, data]):
        return {}
    
    df = pd.DataFrame(data)
    
    if plot_type == 'histogram':
        return px.histogram(df, x=selected_column)
    elif plot_type == 'scatter':
        return px.scatter(df, x=selected_column, y=df.columns[1])
    elif plot_type == 'bar':
        return px.bar(df, x=selected_column, y=df.columns[1])
    elif plot_type == 'pie':
        return px.pie(df, names=selected_column)
    elif plot_type == 'line':
        return px.line(df, x=selected_column, y=df.columns[1])
    return {}

if __name__ == '__main__':
    app.run_server(debug=True)
