import dash
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, ctx, dcc, html

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.themes.LUX], use_pages=True)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Authors", href="http://localhost:8050/")),
        dbc.NavItem(dbc.NavLink("Publications", href="http://localhost:8050/publications")),
    ],
    brand="Medium Dashboard",
    brand_href="http://localhost:8050",
    color="primary",
    dark=True,
)

app.layout = html.Div(
    [
        navbar,
        dash.page_container,
    ],
    className="content",
)

if __name__ == "__main__":
    app.run(debug=True)
