"""
Forest plots for meta-analysis visualization.
"""

import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from typing import Optional, List


def forest_plot(
    effect_sizes: np.ndarray,
    standard_errors: np.ndarray,
    study_names: Optional[List[str]] = None,
    pooled_effect: Optional[float] = None,
    pooled_se: Optional[float] = None,
    title: str = "Forest Plot",
    interactive: bool = True,
    alpha: float = 0.05
) -> Optional[go.Figure]:
    """
    Create a forest plot showing individual study effects and pooled estimate.

    Parameters:
        effect_sizes: Array of effect sizes
        standard_errors: Array of standard errors
        study_names: List of study names
        pooled_effect: Pooled effect estimate
        pooled_se: Standard error of pooled estimate
        title: Plot title
        interactive: If True, return Plotly figure
        alpha: Significance level for confidence intervals

    Returns:
        Plotly figure if interactive=True
    """
    from scipy import stats

    n = len(effect_sizes)
    if study_names is None:
        study_names = [f"Study {i+1}" for i in range(n)]

    # Calculate confidence intervals
    z_crit = stats.norm.ppf(1 - alpha / 2)
    ci_lower = effect_sizes - z_crit * standard_errors
    ci_upper = effect_sizes + z_crit * standard_errors

    if interactive:
        fig = go.Figure()

        # Add individual studies
        for i in range(n):
            # CI line
            fig.add_trace(go.Scatter(
                x=[ci_lower[i], ci_upper[i]],
                y=[i, i],
                mode='lines',
                line=dict(color='gray', width=2),
                showlegend=False,
                hoverinfo='skip'
            ))

            # Point estimate
            fig.add_trace(go.Scatter(
                x=[effect_sizes[i]],
                y=[i],
                mode='markers',
                marker=dict(size=10, color='blue'),
                name=study_names[i],
                hovertemplate=f'<b>{study_names[i]}</b><br>'
                             f'Effect: {effect_sizes[i]:.3f}<br>'
                             f'95% CI: [{ci_lower[i]:.3f}, {ci_upper[i]:.3f}]<extra></extra>',
                showlegend=False
            ))

        # Add pooled estimate
        if pooled_effect is not None and pooled_se is not None:
            pooled_ci_lower = pooled_effect - z_crit * pooled_se
            pooled_ci_upper = pooled_effect + z_crit * pooled_se

            # Diamond for pooled estimate
            y_pooled = -1.5
            fig.add_trace(go.Scatter(
                x=[pooled_ci_lower, pooled_effect, pooled_ci_upper, pooled_effect, pooled_ci_lower],
                y=[y_pooled, y_pooled - 0.3, y_pooled, y_pooled + 0.3, y_pooled],
                fill='toself',
                fillcolor='red',
                line=dict(color='darkred', width=2),
                name=f'Pooled: {pooled_effect:.3f} [{pooled_ci_lower:.3f}, {pooled_ci_upper:.3f}]',
                hovertemplate=f'<b>Pooled Estimate</b><br>'
                             f'Effect: {pooled_effect:.3f}<br>'
                             f'95% CI: [{pooled_ci_lower:.3f}, {pooled_ci_upper:.3f}]<extra></extra>'
            ))

        # Add null effect line
        fig.add_vline(x=0, line_dash="dash", line_color="black", opacity=0.5)

        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title='Effect Size',
            yaxis=dict(
                tickmode='array',
                tickvals=list(range(n)) + ([-1.5] if pooled_effect is not None else []),
                ticktext=study_names + (['Pooled'] if pooled_effect is not None else []),
                autorange='reversed'
            ),
            template='plotly_white',
            height=max(400, n * 30 + 150),
            showlegend=False
        )

        return fig

    else:
        # Matplotlib version
        fig, ax = plt.subplots(figsize=(10, max(6, n * 0.4)))

        y_pos = np.arange(n)

        # Plot CIs
        for i in range(n):
            ax.plot([ci_lower[i], ci_upper[i]], [i, i], 'k-', linewidth=2)
            ax.plot(effect_sizes[i], i, 'bo', markersize=8)

        # Pooled estimate
        if pooled_effect is not None and pooled_se is not None:
            pooled_ci_lower = pooled_effect - z_crit * pooled_se
            pooled_ci_upper = pooled_effect + z_crit * pooled_se

            y_pooled = -1
            ax.plot([pooled_ci_lower, pooled_ci_upper], [y_pooled, y_pooled],
                   'r-', linewidth=3, label='Pooled')
            ax.plot(pooled_effect, y_pooled, 'rd', markersize=12)

        # Null line
        ax.axvline(0, color='gray', linestyle='--', alpha=0.5)

        ax.set_yticks(list(range(n)) + ([-1] if pooled_effect is not None else []))
        ax.set_yticklabels(study_names + (['Pooled'] if pooled_effect is not None else []))
        ax.invert_yaxis()
        ax.set_xlabel('Effect Size')
        ax.set_title(title)
        ax.grid(True, axis='x', alpha=0.3)

        plt.tight_layout()
        plt.show()
        return None
