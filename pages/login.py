"""
Página de login para la aplicación UD Atzeneta Analytics
"""
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from flask_login import login_user, UserMixin
from config import ADMIN_USER, ADMIN_PASSWORD

# Clase para manejar el usuario
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# Función para validar credenciales
def validate_login(username, password):
    """
    Valida las credenciales del usuario
    
    Args:
        username (str): Nombre de usuario
        password (str): Contraseña
        
    Returns:
        User: Objeto User si las credenciales son válidas, None si no
    """
    # En una app real, validaríamos contra la base de datos
    if username == ADMIN_USER and password == ADMIN_PASSWORD:
        user = User(id=1, username=username)
        login_user(user)
        return user
    return None

# Layout de la página de login
def login_layout():
    """
    Crea el layout para la página de login
    """
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        # Logo
                        html.Img(
                            src="/assets/escudo.png",
                            className="img-fluid mx-auto d-block mb-4",
                            style={"maxWidth": "150px"}
                        ),
                        
                        # Título
                        html.H2("UD Atzeneta Analytics", className="text-center mb-4"),
                        
                        # Formulario de login
                        dbc.Card([
                            dbc.CardHeader(html.H4("Iniciar Sesión", className="text-center m-0")),
                            dbc.CardBody([
                                # Usuario
                                dbc.Label("Usuario", html_for="username-input"),
                                dbc.Input(
                                    type="text",
                                    id="username-input",
                                    placeholder="Introduce tu usuario",
                                    className="mb-3"
                                ),
                                
                                # Contraseña
                                dbc.Label("Contraseña", html_for="password-input"),
                                dbc.Input(
                                    type="password",
                                    id="password-input",
                                    placeholder="Introduce tu contraseña",
                                    className="mb-3"
                                ),
                                
                                # Mensaje de error
                                html.Div(id="login-error", className="mb-3"),
                                
                                # Botón de login
                                dbc.Button(
                                    "Acceder",
                                    id="login-button",
                                    color="primary",
                                    className="w-100"
                                ),
                                
                                # Información de demo
                                html.Div([
                                    html.Hr(className="my-3"),
                                    html.P([
                                        "Para la demostración, use: ",
                                        html.Strong("admin / admin")
                                    ], className="text-muted text-center mb-0 small")
                                ])
                            ])
                        ])
                    ], className="login-card")
                ], md=6, lg=4, className="mx-auto")
            ], className="align-items-center min-vh-100")
        ], fluid=True)
    ], className="login-container")