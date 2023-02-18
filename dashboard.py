from dash import Dash, dcc, html, Input, Output, dash_table

import plotly.express as px

import pandas as pd

# datasets
author_df = pd.read_csv('authors.csv')
dataset = pd.read_csv("processed_dataset.csv")

# set author_df columns
column_names = ["Author", "Reading Time (mins)", "Avg. Claps", "Avg. Articles (monthly)", "Publication URL", "Most Published on Single Publication", "Earned (lower bound approx)"]
old_cols = list(author_df.columns)
author_df[column_names] = author_df[old_cols]
author_df.drop(columns=old_cols, inplace=True)
# set dataset dataframe columns
column_names = ["Publication URL", "Author", "Date", "Reading Time (mins)", "Post Title", "Claps"]
old_cols = list(dataset.columns)
dataset[column_names] = dataset[old_cols]
dataset.drop(columns=old_cols, inplace=True)


# dash app configuration
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([

    html.Div([
        html.Div([
        dcc.Input(id='search_bar', value="", type="text", placeholder="Search author..."),
        html.Br(),
        html.Div(
            [dash_table.DataTable(author_df.to_dict('records'), [{"name": i, "id": i} for i in author_df.columns] ) ], 
            id='search_results')
        ]) ]),

    html.Div([
        dcc.Dropdown(author_df.Author.to_list(), "None", id="author-dropdown"),
        html.A("", className="button", id="most-published-pub")
        ]),
    
    html.Div([
        html.Div([], id='article-claps', className='six columns'),
        html.Div([], id='article-reading-time', className='six columns')    
        ])
    
    ])

@app.callback(
        Output("article-reading-time", 'children'),
        Input('author-dropdown', 'value')
)
def article_reading_time(author):
    if author != "None":
        author_entries = dataset[dataset['Author'] == author]
        fig = px.scatter(author_entries, x='Date', y='Reading Time (mins)', color='Publication URL')
        return dcc.Graph("article-reading-time-graph", figure=fig)
    else:
        return dcc.Graph("article-reading-time-graph", figure=px.scatter())


@app.callback(
    Output('article-claps', 'children'),
    Input('author-dropdown', 'value')
)
def article_claps(author):
    if author != 'None':
        fig = px.scatter(dataset[dataset['Author'] == author], x='Date', y='Claps', color='Publication URL')

        return dcc.Graph(id='articles-claps-graph', figure=fig)

    else: 
        return dcc.Graph(id='articles-claps-graph', figure=px.scatter())

@app.callback(
        Output('most-published-pub','children'),
        Input('author-dropdown', 'value')
)
def most_published_pub(author):
    sample = author_df[author_df['Author'] == author]
    return "Most published publication: " + sample["Publication URL"] + " | N: " + str(sample["Most Published on Single Publication"].values[0])

@app.callback(
    Output(component_id='search_results', component_property='children'),
    Input(component_id='search_bar', component_property='value')
)
def search_bar(query):
    L = len(query)
    mask = author_df.Author.apply(lambda x: x[:L]) == query

    result = author_df[mask]

    return dash_table.DataTable(result.to_dict('records'), [{"name": i, "id": i} for i in result.columns])


if __name__ == "__main__":
    app.run_server(debug=True)