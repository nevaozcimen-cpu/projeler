"""Minimal yet feature-rich sample dashboard built with Plotly Dash.

Run with:
    pip install dash plotly pandas numpy
    python app.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from dash import Dash, Input, Output, dash_table, dcc, html
import plotly.express as px


# ---------------------------------------------------------------------------
# Sample dataset
# ---------------------------------------------------------------------------

rng = np.random.default_rng(seed=42)
dates = pd.date_range("2024-01-01", periods=90)
regions = ["North", "South", "East", "West"]

records: list[dict[str, object]] = []
for date in dates:
    for region in regions:
        visitors = rng.integers(500, 2000)
        orders = rng.integers(50, 350)
        revenue = orders * rng.uniform(15, 60)
        records.append(
            {
                "Date": date,
                "Region": region,
                "Visitors": visitors,
                "Orders": orders,
                "Revenue": round(revenue, 2),
                "Conversion Rate": round((orders / visitors) * 100, 2),
                "Avg Basket Size": round(revenue / max(orders, 1), 2),
            }
        )

df = pd.DataFrame.from_records(records)


# ---------------------------------------------------------------------------
# Dash application setup
# ---------------------------------------------------------------------------

app = Dash(__name__)
server = app.server

metric_options = [
    "Revenue",
    "Orders",
    "Visitors",
    "Conversion Rate",
    "Avg Basket Size",
]


def _card(title: str, value_id: str, description: str) -> html.Div:
    return html.Div(
        [
            html.P(title, className="card-title"),
            html.H3(id=value_id, className="card-value"),
            html.Span(description, className="card-desc"),
        ],
        className="card",
    )


app.layout = html.Div(
    [
        html.Header(
            [
                html.H1("E-Commerce Intelligence Dashboard"),
                html.P(
                    "Sample interactive UI built with Plotly Dash "
                    "featuring multiple KPIs and a drill-down table."
                ),
            ],
            className="header",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Metric"),
                        dcc.Dropdown(
                            options=[{"label": m, "value": m} for m in metric_options],
                            value="Revenue",
                            id="metric-dropdown",
                            clearable=False,
                        ),
                    ],
                    className="control",
                ),
                html.Div(
                    [
                        html.Label("Chart Type"),
                        dcc.RadioItems(
                            options=[
                                {"label": "Bar", "value": "bar"},
                                {"label": "Line", "value": "line"},
                            ],
                            value="bar",
                            id="chart-type",
                            inline=True,
                        ),
                    ],
                    className="control",
                ),
                html.Div(
                    [
                        html.Label("Region"),
                        dcc.Dropdown(
                            options=[{"label": r, "value": r} for r in regions] +
                            [{"label": "All", "value": "All"}],
                            value="All",
                            id="region-dropdown",
                            clearable=False,
                        ),
                    ],
                    className="control",
                ),
            ],
            className="controls",
        ),
        html.Section(
            [
                _card("Total Revenue", "total-revenue", "(selected period)"),
                _card("Total Orders", "total-orders", "Completed purchases"),
                _card("Avg Conversion", "avg-conversion", "Across regions"),
            ],
            className="cards",
        ),
        dcc.Graph(id="metric-chart", className="chart"),
        html.Section(
            [
                html.H2("Region Breakdown"),
                dash_table.DataTable(
                    id="region-table",
                    columns=[
                        {"name": c, "id": c} for c in
                        [
                            "Region",
                            "Visitors",
                            "Orders",
                            "Revenue",
                            "Conversion Rate",
                            "Avg Basket Size",
                        ]
                    ],
                    page_size=5,
                    sort_action="native",
                    filter_action="native",
                    style_table={"overflowX": "auto"},
                    style_cell={"padding": "0.5rem", "textAlign": "center"},
                ),
            ],
            className="table-section",
        ),
        html.Footer(
            html.Span(
                "Made with Plotly Dash ? customize freely for your own projects.",
                className="footer-text",
            ),
            className="footer",
        ),
    ],
    className="container",
)


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------


@app.callback(
    Output("metric-chart", "figure"),
    Output("region-table", "data"),
    Output("total-revenue", "children"),
    Output("total-orders", "children"),
    Output("avg-conversion", "children"),
    Input("metric-dropdown", "value"),
    Input("chart-type", "value"),
    Input("region-dropdown", "value"),
)
def update_dashboard(metric: str, chart_type: str, region: str):
    filtered = df.copy()
    if region != "All":
        filtered = filtered[filtered["Region"] == region]

    grouped = filtered.groupby("Date", as_index=False).agg({metric: "sum"})

    fig = px.bar(grouped, x="Date", y=metric, title=f"{metric} Over Time")
    if chart_type == "line":
        fig = px.line(grouped, x="Date", y=metric, title=f"{metric} Over Time")

    fig.update_layout(
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="white",
        margin=dict(l=40, r=20, t=60, b=40),
    )

    summary = filtered.groupby("Region", as_index=False).agg(
        {
            "Visitors": "sum",
            "Orders": "sum",
            "Revenue": "sum",
            "Conversion Rate": "mean",
            "Avg Basket Size": "mean",
        }
    )

    total_revenue = f"$ {summary['Revenue'].sum():,.0f}"
    total_orders = f"{summary['Orders'].sum():,.0f}"
    avg_conversion = f"{summary['Conversion Rate'].mean():.2f} %"

    return fig, summary.to_dict("records"), total_revenue, total_orders, avg_conversion


# ---------------------------------------------------------------------------
# Simple CSS for basic styling
# ---------------------------------------------------------------------------

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Plotly Dash Sample Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            body { font-family: "Segoe UI", sans-serif; margin: 0; background: #f0f2f5; }
            .container { max-width: 1100px; margin: 0 auto; padding: 2rem; }
            .header { margin-bottom: 2rem; }
            .header h1 { margin: 0; font-size: 2rem; }
            .controls { display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem; }
            .control { min-width: 200px; flex: 1; }
            .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                     gap: 1rem; margin-bottom: 2rem; }
            .card { background: white; border-radius: 12px; padding: 1rem 1.5rem;
                    box-shadow: 0 6px 16px rgba(29, 47, 74, 0.1); }
            .card-title { margin: 0; color: #4a5568; font-weight: 600; }
            .card-value { margin: 0.25rem 0; font-size: 1.75rem; color: #1a202c; }
            .card-desc { color: #718096; font-size: 0.9rem; }
            .chart { background: white; border-radius: 12px; padding: 1rem;
                     box-shadow: 0 6px 16px rgba(29, 47, 74, 0.1); margin-bottom: 2rem; }
            .table-section { background: white; border-radius: 12px; padding: 1.5rem;
                             box-shadow: 0 6px 16px rgba(29, 47, 74, 0.1); }
            .table-section h2 { margin-top: 0; }
            .footer { margin-top: 2rem; text-align: center; color: #718096; font-size: 0.85rem; }
            @media (max-width: 768px) {
                .controls { flex-direction: column; }
                .control { width: 100%; }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""


if __name__ == "__main__":
    app.run_server(debug=True)

