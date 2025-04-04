import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output

# Inicializar la aplicación Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Importante: Exporta el servidor para que Gunicorn pueda usarlo
server = app.server

# Diseño de la aplicación
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Mi Aplicación Dash"),
            html.Hr(),
            dcc.Dropdown(
                id='dropdown-example',
                options=[
                    {'label': 'Opción 1', 'value': 'opt1'},
                    {'label': 'Opción 2', 'value': 'opt2'},
                ],
                value='opt1'
            ),
            html.Div(id='output-container')
        ])
    ])
])

# Callbacks
@app.callback(
    Output('output-container', 'children'),
    [Input('dropdown-example', 'value')]
)
def update_output(value):
    return f'Has seleccionado: {value}'

# Esta condición permite ejecutar la app directamente con "python app.py"
if __name__ == '__main__':
    app.run_server(debug=True)