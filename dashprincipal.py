import pandas as pd
import plotly.express as px
import dash
from dash import html, Input, Output, dcc
from dash import dash_table
from database import obtenerestudiantes


def creartablero(server):

    appnotas = dash.Dash(
        __name__,
        server=server,
        url_base_pathname="/dashprincipal/",
        suppress_callback_exceptions=True
    )

    # =======================
    # LAYOUT (SIN BD AL INICIO)
    # =======================
    appnotas.layout = html.Div([

        html.H1("TABLERO AVANZADO",
                style={"textAlign": "center",
                       "backgroundColor": "#1E1BD2",
                       "color": "white",
                       "padding": "20px"}),

        html.Div([
            html.Label("Seleccionar carrera"),

            dcc.Dropdown(
                id="filtro_carrera",
                options=[],
                value=None
            ),

            html.Br(),

            html.Label("Rango de edad"),

            dcc.RangeSlider(
                id="slider_edad",
                min=0,
                max=100,
                step=1,
                value=[0, 100]
            ),

            html.Br(),

            html.Label("Rango promedio"),

            dcc.RangeSlider(
                id="slider_promedio",
                min=0,
                max=5,
                step=0.5,
                value=[0, 5]
            )

        ], style={"width": "80%", "margin": "auto"}),

        html.Br(),

        html.Div(id="kpis", style={"display": "flex", "justifyContent": "space-around"}),

        html.Br(),

        dash_table.DataTable(id="tabla", page_size=8),

        html.Br(),

        dcc.Graph(id="histograma"),
        dcc.Graph(id="dispersion"),
        dcc.Graph(id="pie"),
        dcc.Graph(id="barras")
    ])

    # =======================
    # CARGAR DATOS
    # =======================
    @appnotas.callback(
        Output("tabla", "data"),
        Output("tabla", "columns"),
        Output("kpis", "children"),
        Output("histograma", "figure"),
        Output("dispersion", "figure"),
        Output("pie", "figure"),
        Output("barras", "figure"),
        Output("filtro_carrera", "options"),
        Output("filtro_carrera", "value"),

        Input("slider_edad", "value"),
        Input("slider_promedio", "value")
    )
    def actualizar(rangoedad, rangoprom):

        df = obtenerestudiantes()

        if df is None or df.empty:
            return [], [], [], px.scatter(), px.scatter(), px.pie(), px.bar(), [], None

        opciones = [{"label": c, "value": c} for c in df["Carrera"].unique()]
        carrera_default = opciones[0]["value"]

        filtro = df[
            (df["Edad"] >= rangoedad[0]) &
            (df["Edad"] <= rangoedad[1]) &
            (df["Promedio"] >= rangoprom[0]) &
            (df["Promedio"] <= rangoprom[1])
        ]

        promedio = round(filtro["Promedio"].mean(), 2) if not filtro.empty else 0
        total = len(filtro)

        kpis = [
            html.Div([html.H4("Promedio"), html.H2(promedio)]),
            html.Div([html.H4("Total"), html.H2(total)])
        ]

        histo = px.histogram(filtro, x="Promedio")
        dispersion = px.scatter(filtro, x="Edad", y="Promedio", color="Desempeño")
        pie = px.pie(filtro, names="Desempeño")

        barras = px.bar(
            df.groupby("Carrera")["Promedio"].mean().reset_index(),
            x="Carrera",
            y="Promedio"
        )

        return (
            filtro.to_dict("records"),
            [{"name": i, "id": i} for i in filtro.columns],
            kpis,
            histo,
            dispersion,
            pie,
            barras,
            opciones,
            carrera_default
        )

    return appnotas