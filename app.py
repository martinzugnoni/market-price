import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd

from utils import search_products_in_mercadolibre, get_precio_dolar, currency_format


external_stylesheets = [
    'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css',
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(className='container', children=[
    html.H1('Precio de mercado'),
    html.P(children=[
        html.Span('Esta app es una prueba de concepto desarrollada sobre Python/Pandas, plot.ly y Dash. Utiliza la API de '),
        html.A('Mercado Libre', href='https://developers.mercadolibre.com.ar/es_ar/api-docs-es'),
        html.Span(' (MELI) para determinar el precio de mercado de un artículo en base a una búsqueda de texto.'),
    ]),
    html.P(children=[
        html.Span('Probá realizando búsquedas acotadas, tal como '),
        html.Span("ford focus 2019 0km", className='badge badge-primary'),
        html.Span(' ó '),
        html.Span("iphone 8 plus 64gb usado", className='badge badge-primary'),
    ]),

    html.Div(className='row', children=[
        html.Div(className='col col-12', children=[
            dcc.Input(
                id='search-input',
                placeholder='Ingresá tu búsqueda...',
                className='form-control form-control-lg',
                type='text'
            )
        ]),
        html.Div(className='col col-12', style={'marginTop': '10px'}, children=[
            dcc.Loading(id="loading-1", type="default", children=[
                html.Button('Buscar', id='submit-button', className='btn btn-primary btn-lg')
            ])
        ])

    ]),

    html.Div(className='row', children=[
        html.Div(id='output-state', className='col col-12')
    ]),

    html.Div(className='row', children=[
        html.Div(id='output-plot', className='col col-12')
    ])
])


@app.callback(
    [
        Output("loading-1", "loading_state"),
        Output('output-state', 'children'),
        Output('output-plot', 'children'),
    ],
    [Input('submit-button', 'n_clicks')],
    [State('search-input', 'value')],
)
def update_output_div(n_clicks, input_value):
    if not input_value:
        return ({'is_loading': False}, '', '')

    all_results = search_products_in_mercadolibre({'q': input_value})
    USDARS = get_precio_dolar(blue=True, tipo='venta')
    df_list = []
    for result in all_results:
        if result['currency_id'] == 'ARS':
            price_in_pesos = result['price']
        else:
            price_in_pesos = result['price'] * USDARS
        df_list.append({
            "id": result["id"],
            "price": price_in_pesos,
            "title": result["title"],
        })
    raw_df = pd.DataFrame(df_list)
    rows, columns = raw_df.shape

    from_price = raw_df["price"].quantile(.25)
    to_price = raw_df["price"].quantile(.75)

    filtered_df = raw_df.loc[(raw_df["price"] > from_price) & (raw_df["price"] < to_price)]

    mean_ars = currency_format(filtered_df["price"].mean())
    mean_usd = currency_format(filtered_df['price'].mean() / USDARS)

    output_text = html.Div([
        html.P(f'Se encontraron {rows} publicaciones'),
        html.P(f'Los precios varían mayoritariamente entre ${currency_format(from_price)} y ${currency_format(to_price)}'),
        html.P(f'El precio estimado de mercado es ${mean_ars}'),
        html.P(f'ó su equivalente en dólares US${mean_usd} (tipo de cámbio: ${USDARS})'),
    ])

    output_plot = dcc.Graph(
        id='box-plot',
        figure=go.Figure(
            data=[
                go.Box(
                    name='',
                    x=raw_df['price'],
                    boxpoints='all',
                    jitter=0.3,
                    pointpos=-1.8
                )
            ]
        )
    )

    return ({'is_loading': False}, output_text, output_plot)


if __name__ == '__main__':
    app.run_server(debug=False)
