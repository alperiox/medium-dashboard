import os

import dotenv
from flask_caching import Cache

# data visualization
import plotly.express as px

# dash imports for the dashboard app
import dash
from dash import Input, Output, dash_table, dcc, html

# data processing
import pandas as pd

# load the dotenv
dotenv.load_dotenv("../.env")
DATASET_DIR = os.getenv("DATASET_PATH")
# load the cache
CACHE_CONFIG = {"CACHE_TYPE": "FileSystemCache", "CACHE_DIR": "cache"}
app = dash.get_app()
cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)

# constants for the page
COLUMNS_TO_ROUND = ["average_claps", "average_unique_clappers", "average_reading_time", "average_responses"]

# register the page
dash.register_page(__name__, "/authors")

layout = html.Div(
    [
        html.H1("Authors"),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Input(
                            id="search_bar",
                            value="",
                            type="text",
                            placeholder="Search author...",
                            className="row mx-auto",
                        ),
                        html.Br(className="row"),
                        html.Div([], id="search_results"),
                    ],
                    className="row w-auto border",
                )
            ],
            className="container border border-auto",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div([], className="col-md-6", id="num_articles"),  # bar chart
                        html.Div([], className="col-md-6", id="average_claps"),  # bar chart
                    ],
                    className="row border border-auto",
                ),
                html.Div(
                    [
                        html.Div([], className="col-md-6", id="average_unique_clappers"),  # bar chart
                        html.Div([], className="col-md-6", id="average_responses"),  # bar chart
                    ],
                    className="row border border-auto",
                ),
                html.Div(
                    [
                        html.Div([], className="col-md-4", id="average_reading_time"),  # bar chart
                        html.Div([], className="col-md-4", id="v3_newsletter_subs"),  # bar chart
                        html.Div([], className="col-md-4", id="num_followers"),  # bar chart
                    ],
                    className="row border border-auto",
                ),
            ],
            className="container",
        ),
        dcc.Store("authors_signal"),
        dcc.Store("dataset_signal"),
    ],
    className="container border border-auto",
)


@cache.memoize()
def dataset_global_store():
    dataset = pd.read_csv(os.path.join(DATASET_DIR, "raw_dataset.csv"))
    return dataset.to_json(date_format="iso", orient="split")


@cache.memoize()
def authors_global_store():
    authors = pd.read_csv(os.path.join(DATASET_DIR, "authors_processed.csv"))
    return authors.to_json(date_format="iso", orient="split")


@dash.callback(
    Output(component_id="num_articles", component_property="children"),
    Input("authors_signal", "data"),
)
def num_articles(author_df):
    author_df = authors_global_store()
    author_df = pd.read_json(author_df, orient="split")
    author_df[COLUMNS_TO_ROUND] = author_df[COLUMNS_TO_ROUND].round(2)
    author_df = author_df.sort_values(by="num_articles", ascending=False)
    author_df = author_df.head(10)
    fig = px.bar(author_df, x="author", y="num_articles", title="Number of Articles", color="num_articles", text_auto=".2s")

    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False, showlegend=False)
    fig.update(layout_coloraxis_showscale=False)
    fig.update_layout(xaxis_title="", yaxis_title="Number of Articles")
    return dcc.Graph(figure=fig)


@dash.callback(
    Output(component_id="average_claps", component_property="children"),
    Input("authors_signal", "data"),
)
def average_claps(author_df):
    author_df = authors_global_store()
    author_df = pd.read_json(author_df, orient="split")
    author_df[COLUMNS_TO_ROUND] = author_df[COLUMNS_TO_ROUND].round(2)

    author_df = author_df.sort_values(by="average_claps", ascending=False)
    author_df = author_df.head(10)

    fig = px.bar(author_df, x="author", y="average_claps", title="Average Claps", color="average_claps", text_auto=".2s")
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False, showlegend=False)
    fig.update(layout_coloraxis_showscale=False)
    fig.update_layout(xaxis_title="", yaxis_title="Avg. Claps")
    return dcc.Graph(figure=fig)


@dash.callback(
    Output(component_id="average_unique_clappers", component_property="children"),
    Input("authors_signal", "data"),
)
def average_unique_clappers(author_df):
    author_df = authors_global_store()
    author_df = pd.read_json(author_df, orient="split")
    author_df[COLUMNS_TO_ROUND] = author_df[COLUMNS_TO_ROUND].round(2)

    author_df = author_df.sort_values(by="average_unique_clappers", ascending=False)
    author_df = author_df.head(10)

    fig = px.bar(
        author_df,
        x="author",
        y="average_unique_clappers",
        title="Average Unique Clappers",
        color="average_unique_clappers",
        text_auto=".2s",
    )
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False, showlegend=False)
    fig.update(layout_coloraxis_showscale=False)
    fig.update_layout(xaxis_title="", yaxis_title="Avg. Unique Clappers")
    return dcc.Graph(figure=fig)


@dash.callback(
    Output(component_id="average_responses", component_property="children"),
    Input("authors_signal", "data"),
)
def average_responses(author_df):
    author_df = authors_global_store()
    author_df = pd.read_json(author_df, orient="split")
    author_df[COLUMNS_TO_ROUND] = author_df[COLUMNS_TO_ROUND].round(2)

    author_df = author_df.sort_values(by="average_responses", ascending=False)
    author_df = author_df.head(10)

    fig = px.bar(
        author_df, x="author", y="average_responses", title="Average Responses", color="average_responses", text_auto=".2s"
    )
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False, showlegend=False)
    fig.update(layout_coloraxis_showscale=False)
    fig.update_layout(xaxis_title="", yaxis_title="Avg. Responses")
    return dcc.Graph(figure=fig)


@dash.callback(
    Output(component_id="average_reading_time", component_property="children"),
    Input("authors_signal", "data"),
)
def average_reading_time(author_df):
    author_df = authors_global_store()
    author_df = pd.read_json(author_df, orient="split")
    author_df[COLUMNS_TO_ROUND] = author_df[COLUMNS_TO_ROUND].round(2)
    author_df = author_df.sort_values(by="average_reading_time", ascending=False)
    author_df = author_df.head(10)

    fig = px.bar(
        author_df,
        x="author",
        y="average_reading_time",
        title="Average Reading Time",
        color="average_reading_time",
        text_auto=".2s",
    )
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False, showlegend=False)
    fig.update(layout_coloraxis_showscale=False)
    fig.update_layout(xaxis_title="", yaxis_title="Avg. Reading Time")
    return dcc.Graph(figure=fig)


@dash.callback(
    Output(component_id="v3_newsletter_subs", component_property="children"),
    Input("authors_signal", "data"),
)
def v3_newsletter_subs(author_df):
    author_df = authors_global_store()
    author_df = pd.read_json(author_df, orient="split")
    author_df[COLUMNS_TO_ROUND] = author_df[COLUMNS_TO_ROUND].round(2)
    author_df = author_df.sort_values(by="v3_newsletter_subs", ascending=False)
    author_df = author_df.head(10)

    fig = px.bar(
        author_df, x="author", y="v3_newsletter_subs", title="Newsletter Subscribers", color="v3_newsletter_subs", text_auto=".2s"
    )
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False, showlegend=False)
    fig.update(layout_coloraxis_showscale=False)
    fig.update_layout(xaxis_title="", yaxis_title="Newsletter Subscribers")
    return dcc.Graph(figure=fig)


@dash.callback(
    Output(component_id="num_followers", component_property="children"),
    Input("authors_signal", "data"),
)
def num_followers(author_df):
    author_df = authors_global_store()
    author_df = pd.read_json(author_df, orient="split")
    author_df[COLUMNS_TO_ROUND] = author_df[COLUMNS_TO_ROUND].round(2)
    author_df = author_df.sort_values(by="num_followers", ascending=False)
    author_df = author_df.head(10)

    fig = px.bar(author_df, x="author", y="num_followers", title="Number of Followers", color="num_followers", text_auto=".2s")
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False, showlegend=False)
    fig.update(layout_coloraxis_showscale=False)
    fig.update_layout(xaxis_title="", yaxis_title="Number of Followers")
    return dcc.Graph(figure=fig)


@dash.callback(
    Output(component_id="search_results", component_property="children"),
    Input(component_id="search_bar", component_property="value"),
    Input("authors_signal", "data"),
)
def search_bar(query, author_df):
    author_df = authors_global_store()
    author_df = pd.read_json(author_df, orient="split")
    author_df = author_df.drop(columns=["author_bio", "author_url", "top10pr_tags"])
    author_df = author_df[
        [
            "author",
            "num_articles",
            "num_followers",
            "average_claps",
            "average_unique_clappers",
            "average_reading_time",
            "average_responses",
            "v3_newsletter_subs",
            "membership_date",
        ]
    ]
    COLUMNS_TO_ROUND = ["average_claps", "average_unique_clappers", "average_reading_time", "average_responses"]

    author_df[COLUMNS_TO_ROUND] = author_df[COLUMNS_TO_ROUND].round(2)

    if not query:
        return dash_table.DataTable(
            author_df.to_dict("records"),
            [{"name": i, "id": i} for i in author_df.columns],
            style_table={"overflowX": "auto"},
        )
    else:
        query = " ".join(q.capitalize() for q in query.split())
        query = query.strip()
        L = len(query)
        mask = author_df.author.apply(lambda x: x[:L]) == query

        result = author_df[mask]

        return dash_table.DataTable(
            result.to_dict("records"),
            [{"name": i, "id": i} for i in result.columns],
            style_table={"overflowX": "auto"},
        )
