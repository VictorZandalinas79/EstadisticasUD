import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from database.db_connection import get_league_matches_data

dash.register_page(__name__, path='/kpi', name='KPI Evolución')

def create_evolution_table():
    # Obtener datos
    data = get_league_matches_data()
    
    # Convertir a DataFrame
    df = pd.DataFrame(data)
    
    # Formatear los datos para la tabla
    df['Jornada'] = 'J' + df['match_number'].astype(str)
    df['BLP %'] = df['blp_percentage'].round(2).astype(str) + '%'
    df['Fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%d/%m/%Y')
    
    # Crear las columnas con formato "Jornada (Fecha)"
    df['Jornada_Fecha'] = df['Jornada'] + '\n(' + df['Fecha'] + ')'
    
    # Crear el DataFrame transpuesto con solo BLP%
    metrics = {
        'BLP %': df['BLP %'].tolist()
    }
    
    # Crear el DataFrame final
    final_df = pd.DataFrame(metrics, index=['Valor'])
    final_df.columns = df['Jornada_Fecha']
    final_df = final_df.reset_index()
    
    return dash_table.DataTable(
        id='evolution-table',
        columns=[{"name": str(i), "id": str(i)} for i in final_df.columns],
        data=final_df.to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'whiteSpace': 'pre-line'  # Permite saltos de línea en los encabezados
        },
        style_cell={
            'textAlign': 'center',
            'padding': '10px',
            'minWidth': '100px'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 0},
                'backgroundColor': 'rgba(0, 150, 0, 0.2)'
            }
        ]
    )

layout = html.Div([
    dbc.Container([
        html.H1("Evolución KPIs por Jornada", className="text-center mb-4"),
        
        # Tarjeta informativa
        dbc.Card([
            dbc.CardBody([
                html.H4("BLP - Balón Largo Propio", className="card-title"),
                html.P(
                    "Porcentaje de balones largos propios ganados por el UD Atzeneta "
                    "en segundas jugadas respecto al total de intentos.",
                    className="card-text"
                )
            ])
        ], className="mb-4"),
        
        # Tabla de evolución
        html.Div([
            create_evolution_table()
        ], className="mb-4"),
        
        # Gráfica de evolución
        dcc.Graph(id='evolution-graph')
    ], fluid=True)
])

@callback(
    Output('evolution-graph', 'figure'),
    Input('evolution-table', 'data')
)
def update_graph(data):
    df = pd.DataFrame(data)
    
    # Transformar los datos para la gráfica
    df_melted = pd.melt(df, id_vars=['index'])
    df_melted['value'] = df_melted['value'].str.rstrip('%').astype(float)
    
    fig = px.line(
        df_melted,
        x='variable',
        y='value',
        title='Evolución del BLP por Jornada',
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Jornada",
        yaxis_title="Porcentaje BLP",
        hovermode='x unified'
    )
    
    return fig