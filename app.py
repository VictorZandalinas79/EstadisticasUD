"""
UD Atzeneta Analytics Dashboard
Aplicación principal que gestiona la navegación entre páginas
"""
import dash
from dash import html, dcc, Input, Output, callback, no_update
import dash_bootstrap_components as dbc
from flask import Flask, redirect
from flask_login import LoginManager, current_user, logout_user

# Importar páginas
from pages.login import login_layout, User, validate_login
from pages.home import home_layout, register_home_callbacks, format_evolution_table, get_color_scale, get_color_scale_ocasiones, generar_analisis_kpis
from pages.corners import corners_layout, register_corners_callbacks
from pages.faltas import faltas_layout, register_faltas_callbacks
from pages.momentosjuego import momentosjuego_layout, register_momentosjuego_callbacks
from utils.database import get_all_matches_data, get_dummy_match_data

# Importar configuración
from config import SECRET_KEY, ADMIN_USER, ADMIN_PASSWORD, USE_DUMMY_DATA

# Crear servidor Flask y app Dash
server = Flask(__name__)
server.config['SECRET_KEY'] = SECRET_KEY

app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://use.fontawesome.com/releases/v5.8.1/css/all.css'],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)

# Configurar sistema de login
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

@login_manager.user_loader
def load_user(user_id):
    if user_id == '1':  # Para la demo solo tenemos un usuario admin
        return User(id=1, username=ADMIN_USER)
    return None

# Logout route (debe ser una ruta Flask)
@server.route('/logout')
def logout():
    logout_user()
    return redirect('/login')

# Crear la barra de navegación
def create_navbar():
    return dbc.Navbar(
        dbc.Container([
            # Logo y marca
            dbc.NavbarBrand([
                html.Img(src="/assets/escudo.png", height="40px", className="me-2"),
                html.Img(src="/assets/equipo.png", height="40px", className="me-2"),
                "UD Atzeneta Analytics"
            ], href="/"),
            
            # Botón de hamburguesa para móviles
            dbc.NavbarToggler(id="navbar-toggler"),
            
            # Elementos de navegación
            dbc.Collapse(
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Inicio", href="/")),
                    dbc.NavItem(dbc.NavLink("Corners", href="/corners")),
                    dbc.NavItem(dbc.NavLink("Faltas", href="/faltas")),
                    dbc.NavItem(dbc.NavLink("Momentos de Juego", href="/momentosjuego")),
                    dbc.NavItem(dbc.NavLink("Cerrar Sesión", href="/logout")),
                ], className="ms-auto", navbar=True),
                id="navbar-collapse",
                navbar=True,
                is_open=False,
            ),
        ]),
        color="primary",
        dark=True,
        className="mb-4",
    )

# Layout principal de la aplicación
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Store(id='login-store')
])

# Callback para la navegación
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    """Muestra la página correspondiente según la URL"""
    
    # Si el usuario no está autenticado y no está en login, mostrar página de login
    if not current_user.is_authenticated and pathname != '/login':
        return login_layout()
    
    # Si está en login pero ya está autenticado, ir a home
    if pathname == '/login' and current_user.is_authenticated:
        return html.Div([
            create_navbar(),
            home_layout(),
        ])
    
    # Mostrar la página correspondiente según la URL
    if pathname == '/login':
        return login_layout()
    elif pathname == '/corners':
        return html.Div([
            create_navbar(),
            corners_layout(),
        ])
    elif pathname == '/faltas':
        return html.Div([
            create_navbar(),
            faltas_layout(),
        ])
    elif pathname == '/momentosjuego':
        return html.Div([
            create_navbar(),
            momentosjuego_layout(),
        ])
    else:  # Home o cualquier otra ruta
        return html.Div([
            create_navbar(),
            home_layout(),
        ])

# Callback para manejar el navbar responsive
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [dash.dependencies.State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# Callback para el login
@app.callback(
    [Output('url', 'pathname', allow_duplicate=True),
     Output('login-error', 'children')],
    [Input('login-button', 'n_clicks')],
    [dash.dependencies.State('username-input', 'value'),
     dash.dependencies.State('password-input', 'value')],
    prevent_initial_call=True
)
def login_callback(n_clicks, username, password):
    if not n_clicks:
        return no_update, no_update
    
    if not username or not password:
        return no_update, html.Div("Por favor, introduce usuario y contraseña", className="text-danger")
    
    user = validate_login(username, password)
    if user:
        return '/', no_update
    else:
        return no_update, html.Div("Usuario o contraseña incorrectos", className="text-danger")

# Callback para actualizar la tabla de evolución directamente en app.py
@app.callback(
    [Output('evolution-table', 'data'),
     Output('evolution-table', 'columns'),
     Output('evolution-table', 'style_data_conditional'),
     Output('evolution-table', 'style_header_conditional')],
    [Input('interval-component', 'n_intervals')]
)
def update_table_data(n_intervals):
    """Actualiza la tabla de evolución"""
    try:
        # Intentar obtener datos reales de la base de datos
        data = get_all_matches_data()
        
        # Si no hay datos o hay error, usar datos simulados para pruebas
        if not data and USE_DUMMY_DATA:
            print("No se obtuvieron datos reales. Usando datos simulados...")
            data = get_dummy_match_data()
        
        if data:
            return format_evolution_table(data)
        else:
            print("No se pudieron obtener datos (ni reales ni simulados)")
            return [], [], [], []
            
    except Exception as e:
        print(f"Error al actualizar la tabla: {e}")
        return [], [], [], []

# Callback para el análisis automático
@app.callback(
    Output('analisis-automatico', 'children'),
    [Input('evolution-table', 'data')]
)
def update_analysis(table_data):
    """Actualiza el análisis automático basado en los datos de la tabla"""
    if not table_data:
        return html.Div("No hay datos disponibles para realizar el análisis.")
    
    import pandas as pd
    df = pd.DataFrame(table_data)
    return generar_analisis_kpis(df)

# Registrar callbacks específicos de cada página
# (Nota: Ya estamos manejando los callbacks principales directamente aquí)
register_corners_callbacks(app)
register_faltas_callbacks(app)  # Si tienes callbacks para esta página
register_momentosjuego_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)