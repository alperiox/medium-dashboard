# environment variables
import os

import dash

# dash templates
import dash_bootstrap_components as dbc
import dotenv
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, ctx, dash_table, dcc, html
from flask_caching import Cache
from plotly.subplots import make_subplots

dotenv.load_dotenv("../.env")
DATASET_DIR = os.getenv("DATASET_PATH")
# flask cache

CACHE_CONFIG = {"CACHE_TYPE": "FileSystemCache", "CACHE_DIR": "cache"}
app = dash.get_app()
cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)

dash.register_page(__name__, "/")


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
                dcc.Dropdown([], "None", id="author-dropdown", className="row"),
                html.Div(
                    [
                        html.P(
                            "",
                            className="bg-primary text-white py-4 col text-center border mx-3 w-auto my-auto mx-auto",
                            id="most-published-pub",
                        ),
                        html.P(
                            "",
                            className="bg-primary text-white py-4 col text-center border mx-3 w-auto my-auto mx-auto",
                            id="most-published-pub-counts",
                        ),
                    ],
                    className="row",
                ),
                html.Div([], id="article-reading-time-claps"),
            ],
            className="justify-content-around",
        ),
        dcc.Store("authors_signal"),
        dcc.Store("dataset_signal"),
    ],
    className="container border border-auto ",
)


@cache.memoize()
def dataset_global_store():
    # set dataset dataframe columns
    dataset = pd.read_csv(os.path.join(DATASET_DIR, "processed_dataset.csv"))
    column_names = ["Publication URL", "Author", "Date", "Reading Time (mins)", "Post Title", "Claps"]
    old_cols = list(dataset.columns)
    dataset[column_names] = dataset[old_cols]
    dataset.drop(columns=old_cols, inplace=True)
    return dataset.to_json(date_format="iso", orient="split")


@cache.memoize()
def authors_global_store():  # global store
    # load and return the dataframes
    author_df = pd.read_csv(os.path.join(DATASET_DIR, "authors.csv"))
    # set author_df columns
    column_names = [
        "Author",
        "Reading Time (mins)",
        "Avg. Claps",
        "Avg. Articles (monthly)",
        "Publication URL",
        "Most Published on Single Publication",
        "Earned (lower bound approx)",
    ]
    old_cols = list(author_df.columns)
    author_df[column_names] = author_df[old_cols]
    author_df.drop(columns=old_cols, inplace=True)

    return author_df.to_json(date_format="iso", orient="split")


@dash.callback(Output("author-dropdown", "options"), Input("authors_signal", "data"))
def author_dropdown(author_df):
    author_df = authors_global_store()
    author_df = pd.read_json(author_df, orient="split")
    return author_df.Author.to_list()


@dash.callback(
    Output("article-reading-time-claps", "children"), Input("author-dropdown", "value"), Input("dataset_signal", "data")
)
def author_readingtime_claps_subplots(author, dataset):
    dataset = dataset_global_store()
    dataset = pd.read_json(dataset, orient="split")
    if author != "None":
        author_entries = dataset[dataset["Author"] == author]
        fig = go.Figure()
        colors = px.colors.sequential.Turbo
        publications = set(author_entries["Publication URL"])
        colormap = {pub: colors[idx] for idx, pub in enumerate(publications)}

        # add the traces individually
        for pub in publications:
            pub_entries = author_entries[author_entries["Publication URL"] == pub]
            for idx, rtime in enumerate(pub_entries["Reading Time (mins)"]):
                s = True if idx == 0 else False
                tempdf = pub_entries[pub_entries["Reading Time (mins)"] == rtime]
                fig.add_trace(
                    go.Scatter(
                        x=tempdf["Date"],
                        y=tempdf["Claps"],
                        name=pub,
                        legendgroup=pub,
                        showlegend=s,
                        hovertemplate="Claps: <b>%{y}</b><br>" + f"Time: <b>{rtime} minutes</b><br>" + "Date: %{x}",
                        mode="markers",
                        marker=dict(color=colormap[pub], size=rtime * 2),
                    )
                )

        # finally, update the layout and set the title etc.
        fig.update_layout(
            title="# of Claps & Reading Time",
            xaxis_title="Date",
            yaxis_title="Claps",
        )

        return dcc.Graph("article-readingtime-claps-plot", figure=fig)
    else:
        fig = go.Figure()
        return dcc.Graph("article-readingtime-claps-plot", figure=fig)


@dash.callback(
    Output("most-published-pub", "children"), Input("author-dropdown", "value"), Input("authors_signal", "data")
)
def most_published_pub(author, author_df):
    author_df = authors_global_store()
    author_df = pd.read_json(author_df, orient="split")
    if author != "None":
        sample = author_df[author_df["Author"] == author]
        return "Most published publication: " + sample["Publication URL"]
    else:
        return ""


@dash.callback(
    Output("most-published-pub-counts", "children"), Input("author-dropdown", "value"), Input("authors_signal", "data")
)
def most_published_pub_count(author, author_df):
    author_df = authors_global_store()
    author_df = pd.read_json(author_df, orient="split")
    if author != "None":
        sample = author_df[author_df["Author"] == author]
        return "# of publications: " + str(sample["Most Published on Single Publication"].values[0])
    else:
        return ""


@dash.callback(
    Output(component_id="search_results", component_property="children"),
    Input(component_id="search_bar", component_property="value"),
    Input("authors_signal", "data"),
)
def search_bar(query, author_df):
    author_df = authors_global_store()
    author_df = pd.read_json(author_df, orient="split")
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
        mask = author_df.Author.apply(lambda x: x[:L]) == query

        result = author_df[mask]

        return dash_table.DataTable(
            result.to_dict("records"), [{"name": i, "id": i} for i in result.columns], style_table={"overflowX": "auto"}
        )
