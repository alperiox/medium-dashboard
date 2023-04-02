import os

import dash
import dotenv
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dcc, html
from flask_caching import Cache
from plotly.subplots import make_subplots

dash.register_page(__name__)
dotenv.load_dotenv("../.env")
DATASET_DIR = os.getenv("DATASET_PATH")
# caching
CACHE_CONFIG = {"CACHE_TYPE": "FileSystemCache", "CACHE_DIR": "cache", "CACHE_DEFAULT_TIMEOUT": 300}
app = dash.get_app()
cache = Cache()
cache.init_app(app.server, CACHE_CONFIG)

# page layout
layout = html.Div(
    [
        dcc.Store("dataset_signal"),
        html.H1("Publications"),
        html.Div([], id="num-articles-avg-earnings", className="row"),
        html.Div(
            [
                html.Div([], id="avg-claps", className="col"),
                html.Div([], id="avg-reading-time", className="col"),
            ],
            className="row",
        ),
        html.Div(
            [
                dcc.Dropdown(
                    [], id="publications-dropdown", value=None, placeholder="Select publication", className="col"
                ),
                html.P(
                    "Total articles: ",
                    className="bg-primary text-white py-4 text-center border mx-3 w-auto my-auto mx-auto col",
                    id="publication-total-articles",
                ),
            ],
            className="row",
        ),
        html.Div(
            [html.Div([], id="pub-claps", className="col"), html.Div([], id="pub-reading-time", className="col")],
            className="row",
        ),
    ],
    className="container border",
)


# cache dataset
@cache.memoize()
def dataset_storage():
    # set dataset dataframe columns
    dataset = pd.read_csv(os.path.join(DATASET_DIR, "processed_dataset.csv"))
    return dataset.to_json(date_format="iso", orient="split")


@dash.callback(Output("pub-claps", "children"), Input("publications-dropdown", "value"))
def pub_claps(publication):
    if publication:
        dataset = dataset_storage()
        dataset = pd.read_json(dataset, orient="split")
        df = dataset.query(f"publication_url=='{publication}'")
        fig = px.scatter(df, "date", "claps", title="Claps", labels=dict(date="Date", claps="Claps"))
        fig.update_xaxes()

        return dcc.Graph(figure=fig, id="pub-claps-graph")
    else:
        return dcc.Graph(
            figure=px.scatter(title="Claps", labels=dict(date="Date", claps="Claps")), id="pub-claps-graph"
        )


@dash.callback(Output("pub-reading-time", "children"), Input("publications-dropdown", "value"))
def pub_reading_time(publication):
    if publication:
        dataset = dataset_storage()
        dataset = pd.read_json(dataset, orient="split")
        df = dataset.query(f"publication_url=='{publication}'")
        fig = px.scatter(
            df, "date", "reading_time", title="Reading Time", labels=dict(date="Date", reading_time="Reading time")
        )
        return dcc.Graph(figure=fig, id="pub-reading-time-graph")
    else:
        return dcc.Graph(
            figure=px.scatter(title="Reading Time", labels=dict(date="Date", reading_time="Reading time")),
            id="pub-reading-time-graph",
        )


@dash.callback(Output("publication-total-articles", "children"), Input("publications-dropdown", "value"))
def pub_total_articles(publication):
    if publication:
        dataset = dataset_storage()
        dataset = pd.read_json(dataset, orient="split")
        count = dataset.publication_url.value_counts()[publication]
        return "Total articles: " + str(count)


@dash.callback(Output("publications-dropdown", "options"), Input("dataset_signal", "data"))
def load_dropdown(signal):
    dataset = dataset_storage()
    dataset = pd.read_json(dataset, orient="split")
    return dataset.publication_url.unique().tolist()


@dash.callback(Output("avg-claps", "children"), Input("dataset_signal", "data"))
def avg_claps(signal):
    dataset = pd.read_json(dataset_storage(), orient="split")
    sorted_pubs = sorted(dataset.publication_url.unique())

    avg_claps = (
        dataset.groupby("publication_url").claps.agg(np.mean).reindex(sorted_pubs).reset_index(name="claps").round()
    )

    fig = go.Figure()
    barplot = go.Bar(
        x=avg_claps.publication_url,
        y=avg_claps.claps,
        marker={"color": px.colors.qualitative.Plotly},
        texttemplate="%{y}",
        hovertemplate="publication: <b>%{x}</b>",
    )
    fig.add_trace(barplot)
    fig.update_layout(xaxis={"showticklabels": False}, title_text="Average claps")
    # fig = px.bar(avg_claps, x='publication_url', y='claps', color=px.colors.qualitative.Plotly[:len(sorted_pubs)],
    #             title='Average claps', text_auto=".2s",
    #             category_orders={'color': sorted_pubs})

    return dcc.Graph(figure=fig, id="avg-claps-graph")


@dash.callback(Output("avg-reading-time", "children"), Input("dataset_signal", "data"))
def avg_reading_time(signal):
    dataset = pd.read_json(dataset_storage(), orient="split")
    sorted_pubs = sorted(dataset.publication_url.unique())

    avg_reading_time = (
        dataset.groupby("publication_url")
        .reading_time.agg(np.mean)
        .reindex(sorted_pubs)
        .reset_index(name="reading_time")
        .round()
    )

    fig = go.Figure()
    barplot = go.Bar(
        x=avg_reading_time.publication_url,
        y=avg_reading_time.reading_time,
        marker={"color": px.colors.qualitative.Plotly},
        texttemplate="%{y}",
        hovertemplate="publication: <b>%{x}</b>",
    )
    fig.add_trace(barplot)
    fig.update_layout(xaxis={"showticklabels": False}, title_text="Average reading time")

    return dcc.Graph(figure=fig, id="avg-reading-time-graph")


@dash.callback(Output("num-articles-avg-earnings", "children"), Input("dataset_signal", "data"))
def num_articles_avg_earnings(signal):
    dataset = pd.read_json(dataset_storage(), orient="split")

    num_articles = (
        dataset.publication_url.value_counts()
        .reindex(sorted(dataset.publication_url.unique()))
        .reset_index(name="num_articles")
    )
    num_articles["publication"] = num_articles["index"]
    num_articles.drop(columns="index", inplace=True)

    earnings_group = (
        dataset.groupby("publication_url")
        .claps.agg(sum)
        .reindex(sorted(dataset.publication_url.unique()))
        .reset_index(name="claps")
    )
    earnings_group["claps"] = earnings_group["claps"] * 0.1

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=["Number of published articles", "Average earnings"],
        specs=[[{"type": "bar"}, {"type": "pie"}]],
    )

    barplot = go.Bar(
        x=num_articles.publication,
        y=num_articles.num_articles,
        showlegend=False,
        hovertemplate="Publication: <b>%{x}</b><br># articles: <b>%{y}</b>",
        marker={"color": px.colors.qualitative.Plotly},
        texttemplate="%{y}",
    )

    pieplot = go.Pie(
        labels=earnings_group.publication_url,
        values=earnings_group.claps.round(),
        marker={"colors": px.colors.qualitative.Plotly},
        sort=False,
    )
    pieplot.update(textinfo="value")

    fig.add_trace(barplot, 1, 1)
    fig.add_trace(pieplot, 1, 2)
    fig.update_layout(xaxis={"showticklabels": False})

    return dcc.Graph(id="avg-earnings-graph", figure=fig)
