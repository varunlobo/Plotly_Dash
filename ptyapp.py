import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import base64
import io

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server  # Required for AWS deployment

# Define the layout
app.layout = html.Div([
    html.H1("📊 CSV File Visualizer", style={"text-align": "center", "color": "#2c3e50"}),

    dcc.Upload(
        id='upload-data',
        children=html.Button("Upload CSV", style={"background-color": "#3498db", "color": "white",
                                                  "padding": "10px", "border-radius": "5px",
                                                  "font-size": "16px", "cursor": "pointer"}),
        multiple=False,
        style={"text-align": "center", "margin-bottom": "20px"}
    ),

    html.Div(id='output-data-upload')
], style={"max-width": "800px", "margin": "auto", "font-family": "Arial"})

# Function to parse CSV
def parse_contents(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    return df

# Callback for handling file upload
@app.callback(
    Output('output-data-upload', 'children'),
    Input('upload-data', 'contents')
)
def update_output(contents):
    if contents is None:
        return html.P("Upload a CSV file to see the plots.", style={"text-align": "center", "color": "#e74c3c"})

    df = parse_contents(contents)

    # Display table preview
    table = dash_table.DataTable(
        data=df.head().to_dict("records"),
        columns=[{"name": i, "id": i} for i in df.columns],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '5px'},
        style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'}
    )

    # Generate plots
    plots = []
    numeric_cols = df.select_dtypes(include=['number']).columns
    if not numeric_cols.empty:
        for column in numeric_cols:
            plots.append(dcc.Graph(figure=px.histogram(df, x=column, title=f"Distribution of {column}")))

        if len(numeric_cols) >= 2:
            plots.append(dcc.Graph(figure=px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                                                     title=f"Scatter Plot: {numeric_cols[0]} vs {numeric_cols[1]}")))
            plots.append(dcc.Graph(figure=px.box(df, y=numeric_cols[0], title=f"Box Plot of {numeric_cols[0]}")))

    return html.Div([html.H3("📋 Data Preview"), table, html.H3("📈 Generated Plots")] + plots)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
