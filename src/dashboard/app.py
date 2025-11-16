"""
Main dashboard application for publication bias assessment.

This module creates an interactive web-based dashboard for comprehensive
publication bias assessment using multiple methods.
"""

import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Optional
import io
import base64

from ..methods import (
    egger_test, begg_test, trim_and_fill, pet_peese_combined,
    copas_model, vevea_hedges_model, maive_estimator
)
from ..visualization import (
    contour_enhanced_funnel_plot, trim_fill_funnel_plot,
    comparison_funnel_plot, forest_plot
)
from ..utils.data_utils import MetaAnalysisData, simulate_publication_bias_data
from ..utils.statistics import random_effects_model


class PublicationBiasDashboard:
    """
    Interactive dashboard for publication bias assessment.

    Provides a comprehensive interface for:
    - Data upload and exploration
    - Multiple publication bias tests
    - Visual diagnostics (funnel plots, forest plots)
    - Method comparison
    - Result export
    """

    def __init__(self, data: Optional[MetaAnalysisData] = None):
        """
        Initialize dashboard.

        Parameters:
            data: Optional MetaAnalysisData object. If None, demo data will be used.
        """
        self.data = data
        self.app = self._create_app()
        self._setup_callbacks()

    def _create_app(self) -> dash.Dash:
        """Create Dash application with layout."""
        app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            suppress_callback_exceptions=True
        )

        app.layout = self._create_layout()
        return app

    def _create_layout(self) -> html.Div:
        """Create dashboard layout."""
        return dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1("Multi-Method Publication Bias Assessment Dashboard",
                           className="text-center mb-4 mt-4"),
                    html.Hr()
                ])
            ]),

            # Data Upload Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H4("1. Data Input")),
                        dbc.CardBody([
                            dbc.Tabs([
                                dbc.Tab(label="Upload Data", tab_id="upload",
                                       children=[
                                           html.Div([
                                               dcc.Upload(
                                                   id='upload-data',
                                                   children=html.Div([
                                                       'Drag and Drop or ',
                                                       html.A('Select CSV File')
                                                   ]),
                                                   style={
                                                       'width': '100%',
                                                       'height': '60px',
                                                       'lineHeight': '60px',
                                                       'borderWidth': '1px',
                                                       'borderStyle': 'dashed',
                                                       'borderRadius': '5px',
                                                       'textAlign': 'center',
                                                       'margin': '10px'
                                                   }
                                               ),
                                               html.Div(id='upload-status')
                                           ])
                                       ]),
                                dbc.Tab(label="Simulate Data", tab_id="simulate",
                                       children=[
                                           html.Div([
                                               dbc.Row([
                                                   dbc.Col([
                                                       dbc.Label("Number of Studies"),
                                                       dbc.Input(id="n-studies", type="number",
                                                               value=50, min=10, max=200)
                                                   ]),
                                                   dbc.Col([
                                                       dbc.Label("True Effect"),
                                                       dbc.Input(id="true-effect", type="number",
                                                               value=0.3, step=0.1)
                                                   ])
                                               ], className="mb-3"),
                                               dbc.Row([
                                                   dbc.Col([
                                                       dbc.Label("Heterogeneity (τ)"),
                                                       dbc.Input(id="heterogeneity", type="number",
                                                               value=0.1, step=0.05, min=0)
                                                   ]),
                                                   dbc.Col([
                                                       dbc.Label("Bias Severity"),
                                                       dbc.Select(id="bias-severity",
                                                                options=[
                                                                    {"label": "None", "value": "none"},
                                                                    {"label": "Mild", "value": "mild"},
                                                                    {"label": "Moderate", "value": "moderate"},
                                                                    {"label": "Severe", "value": "severe"}
                                                                ],
                                                                value="moderate")
                                                   ])
                                               ], className="mb-3"),
                                               dbc.Button("Generate Data", id="generate-btn",
                                                        color="primary", className="mt-2")
                                           ], style={"padding": "10px"})
                                       ])
                            ], id="data-tabs", active_tab="simulate")
                        ])
                    ], className="mb-4")
                ])
            ]),

            # Data Preview
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H4("Data Preview")),
                        dbc.CardBody([
                            html.Div(id='data-preview')
                        ])
                    ], className="mb-4")
                ])
            ]),

            # Analysis Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H4("2. Run Analyses")),
                        dbc.CardBody([
                            dbc.Checklist(
                                id="methods-checklist",
                                options=[
                                    {"label": " Egger's Test", "value": "egger"},
                                    {"label": " Begg's Test", "value": "begg"},
                                    {"label": " Trim-and-Fill", "value": "trim_fill"},
                                    {"label": " PET-PEESE", "value": "pet_peese"},
                                    {"label": " Copas Selection Model", "value": "copas"},
                                    {"label": " Vevea-Hedges Model", "value": "vevea"},
                                    {"label": " MAIVE Estimator", "value": "maive"}
                                ],
                                value=["egger", "begg", "trim_fill", "pet_peese", "maive"],
                                inline=False,
                                className="mb-3"
                            ),
                            dbc.Button("Run Selected Methods", id="run-analysis-btn",
                                     color="success", size="lg", className="w-100")
                        ])
                    ], className="mb-4")
                ])
            ]),

            # Results Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H4("3. Results")),
                        dbc.CardBody([
                            dbc.Tabs([
                                dbc.Tab(label="Summary Table", tab_id="summary",
                                       children=[html.Div(id='results-summary')]),
                                dbc.Tab(label="Funnel Plots", tab_id="funnel",
                                       children=[html.Div(id='funnel-plots')]),
                                dbc.Tab(label="Forest Plot", tab_id="forest",
                                       children=[html.Div(id='forest-plot')]),
                                dbc.Tab(label="Method Comparison", tab_id="comparison",
                                       children=[html.Div(id='method-comparison')]),
                                dbc.Tab(label="Detailed Results", tab_id="detailed",
                                       children=[html.Div(id='detailed-results')])
                            ], id="results-tabs")
                        ])
                    ])
                ])
            ]),

            # Hidden div to store data
            dcc.Store(id='stored-data'),
            dcc.Store(id='analysis-results')

        ], fluid=True, style={"maxWidth": "1400px"})

    def _setup_callbacks(self):
        """Setup all dashboard callbacks."""

        @self.app.callback(
            Output('stored-data', 'data'),
            Output('upload-status', 'children'),
            Input('generate-btn', 'n_clicks'),
            Input('upload-data', 'contents'),
            State('n-studies', 'value'),
            State('true-effect', 'value'),
            State('heterogeneity', 'value'),
            State('bias-severity', 'value'),
            State('upload-data', 'filename'),
            prevent_initial_call=True
        )
        def load_data(n_clicks_gen, upload_contents, n_studies, true_effect,
                     heterogeneity, bias_severity, filename):
            """Load or generate data."""
            ctx = dash.callback_context

            if not ctx.triggered:
                return None, ""

            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

            if trigger_id == 'generate-btn':
                # Generate simulated data
                data = simulate_publication_bias_data(
                    n_studies=n_studies,
                    true_effect=true_effect,
                    heterogeneity=heterogeneity,
                    bias_severity=bias_severity,
                    random_seed=42
                )

                data_dict = {
                    'effect_sizes': data.effect_sizes.tolist(),
                    'standard_errors': data.standard_errors.tolist(),
                    'study_names': data.study_names
                }

                return data_dict, dbc.Alert(
                    f"✓ Generated {len(data.effect_sizes)} studies with {bias_severity} bias",
                    color="success"
                )

            elif trigger_id == 'upload-data' and upload_contents:
                # Parse uploaded file
                content_type, content_string = upload_contents.split(',')
                decoded = base64.b64decode(content_string)

                try:
                    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

                    # Assume columns: effect_size, se (or stderr, or standard_error)
                    effect_col = [c for c in df.columns if 'effect' in c.lower()][0]
                    se_cols = [c for c in df.columns if 'se' in c.lower() or 'std' in c.lower()]
                    se_col = se_cols[0] if se_cols else 'se'

                    data_dict = {
                        'effect_sizes': df[effect_col].tolist(),
                        'standard_errors': df[se_col].tolist(),
                        'study_names': df.iloc[:, 0].tolist() if df.shape[1] > 2 else None
                    }

                    return data_dict, dbc.Alert(
                        f"✓ Loaded {len(df)} studies from {filename}",
                        color="success"
                    )

                except Exception as e:
                    return None, dbc.Alert(f"✗ Error loading file: {str(e)}", color="danger")

            return None, ""

        @self.app.callback(
            Output('data-preview', 'children'),
            Input('stored-data', 'data')
        )
        def preview_data(data_dict):
            """Display data preview."""
            if not data_dict:
                return html.P("No data loaded. Please upload or generate data.",
                            className="text-muted")

            df = pd.DataFrame({
                'Study': data_dict.get('study_names', [f"Study {i+1}" for i in range(len(data_dict['effect_sizes']))]),
                'Effect Size': data_dict['effect_sizes'],
                'Std Error': data_dict['standard_errors']
            })

            return dash_table.DataTable(
                data=df.head(10).to_dict('records'),
                columns=[{"name": i, "id": i} for i in df.columns],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '10px'},
                style_header={'backgroundColor': 'lightgray', 'fontWeight': 'bold'}
            )

        @self.app.callback(
            Output('analysis-results', 'data'),
            Input('run-analysis-btn', 'n_clicks'),
            State('stored-data', 'data'),
            State('methods-checklist', 'value'),
            prevent_initial_call=True
        )
        def run_analyses(n_clicks, data_dict, selected_methods):
            """Run selected publication bias methods."""
            if not data_dict or not selected_methods:
                return None

            effect_sizes = np.array(data_dict['effect_sizes'])
            standard_errors = np.array(data_dict['standard_errors'])
            variances = standard_errors ** 2

            results = {}

            # Run random-effects model
            pooled_effect, pooled_se, tau2, I2 = random_effects_model(
                effect_sizes, variances
            )
            results['pooled'] = {
                'effect': pooled_effect,
                'se': pooled_se,
                'tau2': tau2,
                'I2': I2
            }

            # Run selected methods
            if 'egger' in selected_methods:
                egger_result = egger_test(effect_sizes, standard_errors)
                results['egger'] = {
                    'intercept': egger_result.intercept,
                    'p_value': egger_result.p_value,
                    'significant': egger_result.significant
                }

            if 'begg' in selected_methods:
                begg_result = begg_test(effect_sizes, variances)
                results['begg'] = {
                    'tau': begg_result.tau,
                    'p_value': begg_result.p_value,
                    'significant': begg_result.significant
                }

            if 'trim_fill' in selected_methods:
                tf_result = trim_and_fill(effect_sizes, variances)
                results['trim_fill'] = {
                    'n_missing': tf_result.n_missing,
                    'adjusted_effect': tf_result.adjusted_effect,
                    'adjusted_se': tf_result.adjusted_se,
                    'filled_effects': tf_result.filled_effect_sizes.tolist(),
                    'filled_se': np.sqrt(tf_result.filled_variances).tolist()
                }

            if 'pet_peese' in selected_methods:
                pp_result = pet_peese_combined(effect_sizes, standard_errors,
                                              bootstrap=True, n_bootstrap=500)
                results['pet_peese'] = {
                    'selected_method': pp_result.selected_method,
                    'estimate': pp_result.selected_estimate,
                    'ci': pp_result.selected_ci,
                    'bootstrap_ci': pp_result.bootstrap_ci
                }

            if 'copas' in selected_methods:
                copas_result = copas_model(effect_sizes, standard_errors)
                results['copas'] = {
                    'adjusted_effect': copas_result.adjusted_effect,
                    'adjusted_se': copas_result.adjusted_se,
                    'rho': copas_result.rho
                }

            if 'vevea' in selected_methods:
                vevea_result = vevea_hedges_model(effect_sizes, variances)
                results['vevea'] = {
                    'adjusted_effect': vevea_result.adjusted_effect,
                    'adjusted_se': vevea_result.adjusted_se
                }

            if 'maive' in selected_methods:
                maive_result = maive_estimator(effect_sizes, standard_errors)
                results['maive'] = {
                    'effect': maive_result.maive_effect,
                    'se': maive_result.maive_se,
                    'iv_strength': maive_result.iv_strength
                }

            return results

        @self.app.callback(
            Output('results-summary', 'children'),
            Input('analysis-results', 'data')
        )
        def display_summary(results):
            """Display summary table of results."""
            if not results:
                return html.P("No results yet. Run analyses first.", className="text-muted")

            # Create summary table
            summary_data = []

            # Original pooled estimate
            pooled = results.get('pooled', {})
            summary_data.append({
                'Method': 'Random Effects (Original)',
                'Estimate': f"{pooled.get('effect', 0):.4f}",
                'Std Error': f"{pooled.get('se', 0):.4f}",
                'Bias Detected': 'N/A'
            })

            # Egger's test
            if 'egger' in results:
                egger = results['egger']
                summary_data.append({
                    'Method': "Egger's Test",
                    'Estimate': 'N/A',
                    'Std Error': 'N/A',
                    'Bias Detected': '✓ Yes' if egger['significant'] else '✗ No'
                })

            # Begg's test
            if 'begg' in results:
                begg = results['begg']
                summary_data.append({
                    'Method': "Begg's Test",
                    'Estimate': 'N/A',
                    'Std Error': 'N/A',
                    'Bias Detected': '✓ Yes' if begg['significant'] else '✗ No'
                })

            # Trim-and-fill
            if 'trim_fill' in results:
                tf = results['trim_fill']
                summary_data.append({
                    'Method': f"Trim-and-Fill ({tf['n_missing']} missing)",
                    'Estimate': f"{tf['adjusted_effect']:.4f}",
                    'Std Error': f"{tf['adjusted_se']:.4f}",
                    'Bias Detected': '✓ Yes' if tf['n_missing'] > 0 else '✗ No'
                })

            # PET-PEESE
            if 'pet_peese' in results:
                pp = results['pet_peese']
                summary_data.append({
                    'Method': f"PET-PEESE ({pp['selected_method']})",
                    'Estimate': f"{pp['estimate']:.4f}",
                    'Std Error': 'N/A',
                    'Bias Detected': '✓ Yes'
                })

            # MAIVE
            if 'maive' in results:
                maive = results['maive']
                summary_data.append({
                    'Method': f"MAIVE (F={maive['iv_strength']:.1f})",
                    'Estimate': f"{maive['effect']:.4f}",
                    'Std Error': f"{maive['se']:.4f}",
                    'Bias Detected': '✓ Yes'
                })

            df_summary = pd.DataFrame(summary_data)

            return dash_table.DataTable(
                data=df_summary.to_dict('records'),
                columns=[{"name": i, "id": i} for i in df_summary.columns],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '12px'},
                style_header={
                    'backgroundColor': '#2c3e50',
                    'color': 'white',
                    'fontWeight': 'bold'
                },
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{Bias Detected} contains "✓"'},
                        'backgroundColor': '#ffe6e6'
                    },
                    {
                        'if': {'filter_query': '{Bias Detected} contains "✗"'},
                        'backgroundColor': '#e6ffe6'
                    }
                ]
            )

        @self.app.callback(
            Output('funnel-plots', 'children'),
            Input('analysis-results', 'data'),
            State('stored-data', 'data')
        )
        def display_funnel_plots(results, data_dict):
            """Display funnel plots."""
            if not results or not data_dict:
                return html.P("No results to display.", className="text-muted")

            effect_sizes = np.array(data_dict['effect_sizes'])
            standard_errors = np.array(data_dict['standard_errors'])
            study_names = data_dict.get('study_names')

            pooled_effect = results['pooled']['effect']

            plots = []

            # Contour-enhanced funnel plot
            fig1 = contour_enhanced_funnel_plot(
                effect_sizes, standard_errors, study_names,
                pooled_effect, interactive=True
            )
            plots.append(dcc.Graph(figure=fig1, className="mb-4"))

            # Trim-and-fill funnel plot
            if 'trim_fill' in results:
                tf = results['trim_fill']
                filled_effects = np.array(tf['filled_effects'])
                filled_se = np.array(tf['filled_se'])

                fig2 = trim_fill_funnel_plot(
                    effect_sizes, standard_errors,
                    filled_effects, filled_se,
                    study_names,
                    pooled_effect,
                    tf['adjusted_effect'],
                    interactive=True
                )
                plots.append(dcc.Graph(figure=fig2))

            return html.Div(plots)

        @self.app.callback(
            Output('method-comparison', 'children'),
            Input('analysis-results', 'data'),
            State('stored-data', 'data')
        )
        def display_comparison(results, data_dict):
            """Display method comparison plot."""
            if not results or not data_dict:
                return html.P("No results to display.", className="text-muted")

            effect_sizes = np.array(data_dict['effect_sizes'])
            standard_errors = np.array(data_dict['standard_errors'])
            study_names = data_dict.get('study_names')

            # Collect estimates from different methods
            methods_results = {
                'Original': results['pooled']['effect']
            }

            if 'trim_fill' in results:
                methods_results['Trim-Fill'] = results['trim_fill']['adjusted_effect']

            if 'pet_peese' in results:
                methods_results['PET-PEESE'] = results['pet_peese']['estimate']

            if 'maive' in results:
                methods_results['MAIVE'] = results['maive']['effect']

            fig = comparison_funnel_plot(
                effect_sizes, standard_errors,
                methods_results, study_names,
                interactive=True
            )

            return dcc.Graph(figure=fig)

    def run(self, debug=False, port=8050):
        """
        Run the dashboard server.

        Parameters:
            debug: Enable debug mode
            port: Port number for server
        """
        self.app.run_server(debug=debug, port=port)


def create_dashboard(data: Optional[MetaAnalysisData] = None, **kwargs):
    """
    Create and launch publication bias dashboard.

    Parameters:
        data: Optional MetaAnalysisData object
        **kwargs: Additional arguments passed to dashboard.run()

    Returns:
        PublicationBiasDashboard instance
    """
    dashboard = PublicationBiasDashboard(data)
    return dashboard
