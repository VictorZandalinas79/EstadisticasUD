import dash
from dash import html

app = dash.Dash(__name__)
server = app.server  # Esto es lo que Gunicorn utilizará

app.layout = html.Div("Test de UD Atzeneta Analytics - App simplificada")

if __name__ == '__main__':
    app.run_server(debug=True)