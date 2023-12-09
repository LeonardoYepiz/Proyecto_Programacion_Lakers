import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, dash_table, callback, Input, Output

data_asistentes = pd.read_csv("C:/Users/may11/Downloads/asistentes.csv")

def dashboard():
    body = html.Div([
        html.H2("Datos de Asistentes"),
        html.P("Objetivo del DashBoard: Mostrar los datos de los asistentes."),
        html.Hr(),
        dcc.Dropdown(
            id="ddAsistentes",
            options=[
                {"label": asistente, "value": asistente} for asistente in data_asistentes["Nombre"]
            ],
            multi=True,
            value=[data_asistentes["Nombre"].iloc[0]],
            style={'width': '50%'}
        ),
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in data_asistentes.columns],
            data=data_asistentes.to_dict("records"),
            page_size=10
        ),
        dcc.Graph(id="figAsistentes")
    ])
    return body

@callback(
    Output("figAsistentes", "figure"),
    Input("ddAsistentes", "value")
)
def update_grafica(selected_asistentes):
    filtered_data = data_asistentes[data_asistentes["Nombre"].isin(selected_asistentes)]
    fig = px.line(filtered_data, x="Nombre", y="Cargo", title="Cargos de Asistentes")
    return fig


if __name__ == "__main__":
    app = Dash(__name__)
    app.layout = dashboard()
    app.run_server(debug=True, host='127.0.0.1', port=8050)
