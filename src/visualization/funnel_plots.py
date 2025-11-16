"""
Enhanced funnel plot visualizations for publication bias assessment.

Funnel plots display effect sizes against their standard errors (or precision).
In the absence of publication bias, the plot should resemble a symmetric funnel.
"""

import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from typing import Optional, Tuple, List
import warnings


def funnel_plot(
    effect_sizes: np.ndarray,
    standard_errors: np.ndarray,
    study_names: Optional[List[str]] = None,
    pooled_effect: Optional[float] = None,
    title: str = "Funnel Plot",
    interactive: bool = False,
    **kwargs
) -> Optional[go.Figure]:
    """
    Basic funnel plot.

    Parameters:
        effect_sizes: Array of effect sizes
        standard_errors: Array of standard errors
        study_names: List of study names for labeling
        pooled_effect: Pooled effect estimate (vertical line)
        title: Plot title
        interactive: If True, return interactive Plotly figure, else Matplotlib
        **kwargs: Additional plotting arguments

    Returns:
        Plotly figure if interactive=True, else None (shows matplotlib plot)
    """
    if study_names is None:
        study_names = [f"Study {i+1}" for i in range(len(effect_sizes))]

    if interactive:
        return _funnel_plot_plotly(
            effect_sizes, standard_errors, study_names, pooled_effect, title
        )
    else:
        _funnel_plot_matplotlib(
            effect_sizes, standard_errors, study_names, pooled_effect, title, **kwargs
        )
        return None


def _funnel_plot_matplotlib(
    effect_sizes: np.ndarray,
    standard_errors: np.ndarray,
    study_names: List[str],
    pooled_effect: Optional[float],
    title: str,
    **kwargs
):
    """Matplotlib implementation of funnel plot."""
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot studies
    ax.scatter(effect_sizes, standard_errors, alpha=0.6, s=100, **kwargs)

    # Add pooled effect line
    if pooled_effect is not None:
        ax.axvline(pooled_effect, color='red', linestyle='--', linewidth=2,
                   label=f'Pooled Effect: {pooled_effect:.3f}')

    # Add confidence funnel (pseudo-confidence intervals)
    if pooled_effect is not None:
        se_range = np.linspace(0, max(standard_errors) * 1.1, 100)
        ci_lower = pooled_effect - 1.96 * se_range
        ci_upper = pooled_effect + 1.96 * se_range

        ax.plot(ci_lower, se_range, 'k--', alpha=0.3, linewidth=1)
        ax.plot(ci_upper, se_range, 'k--', alpha=0.3, linewidth=1)
        ax.fill_betweenx(se_range, ci_lower, ci_upper, alpha=0.1, color='gray')

    # Invert y-axis (higher precision at top)
    ax.invert_yaxis()

    ax.set_xlabel('Effect Size', fontsize=12)
    ax.set_ylabel('Standard Error', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def _funnel_plot_plotly(
    effect_sizes: np.ndarray,
    standard_errors: np.ndarray,
    study_names: List[str],
    pooled_effect: Optional[float],
    title: str
) -> go.Figure:
    """Plotly implementation of funnel plot."""
    fig = go.Figure()

    # Add confidence funnel
    if pooled_effect is not None:
        se_range = np.linspace(0, max(standard_errors) * 1.1, 100)
        ci_lower = pooled_effect - 1.96 * se_range
        ci_upper = pooled_effect + 1.96 * se_range

        # 95% CI region
        fig.add_trace(go.Scatter(
            x=np.concatenate([ci_lower, ci_upper[::-1]]),
            y=np.concatenate([se_range, se_range[::-1]]),
            fill='toself',
            fillcolor='rgba(128, 128, 128, 0.2)',
            line=dict(color='rgba(128, 128, 128, 0)'),
            name='95% CI',
            hoverinfo='skip'
        ))

        # Pooled effect line
        fig.add_trace(go.Scatter(
            x=[pooled_effect, pooled_effect],
            y=[0, max(standard_errors) * 1.1],
            mode='lines',
            line=dict(color='red', dash='dash', width=2),
            name=f'Pooled: {pooled_effect:.3f}'
        ))

    # Add studies
    fig.add_trace(go.Scatter(
        x=effect_sizes,
        y=standard_errors,
        mode='markers',
        marker=dict(size=10, color='blue', opacity=0.6),
        text=study_names,
        hovertemplate='<b>%{text}</b><br>Effect: %{x:.3f}<br>SE: %{y:.3f}<extra></extra>',
        name='Studies'
    ))

    fig.update_layout(
        title=title,
        xaxis_title='Effect Size',
        yaxis_title='Standard Error',
        yaxis=dict(autorange='reversed'),
        hovermode='closest',
        template='plotly_white',
        height=600
    )

    return fig


def contour_enhanced_funnel_plot(
    effect_sizes: np.ndarray,
    standard_errors: np.ndarray,
    study_names: Optional[List[str]] = None,
    pooled_effect: Optional[float] = None,
    title: str = "Contour-Enhanced Funnel Plot",
    interactive: bool = True
) -> go.Figure:
    """
    Contour-enhanced funnel plot with significance contours.

    Adds shaded regions corresponding to p-value thresholds (0.01, 0.05, 0.10).
    Helps identify if studies are concentrated in significant regions.

    Parameters:
        effect_sizes: Array of effect sizes
        standard_errors: Array of standard errors
        study_names: List of study names
        pooled_effect: Pooled effect estimate
        title: Plot title
        interactive: If True, return Plotly figure

    Returns:
        Plotly figure
    """
    if study_names is None:
        study_names = [f"Study {i+1}" for i in range(len(effect_sizes))]

    if pooled_effect is None:
        pooled_effect = np.mean(effect_sizes)

    fig = go.Figure()

    # Create contour regions for different significance levels
    se_range = np.linspace(0, max(standard_errors) * 1.2, 200)

    # p < 0.01 (z = 2.576)
    contour_01_lower = pooled_effect - 2.576 * se_range
    contour_01_upper = pooled_effect + 2.576 * se_range

    # p < 0.05 (z = 1.96)
    contour_05_lower = pooled_effect - 1.96 * se_range
    contour_05_upper = pooled_effect + 1.96 * se_range

    # p < 0.10 (z = 1.645)
    contour_10_lower = pooled_effect - 1.645 * se_range
    contour_10_upper = pooled_effect + 1.645 * se_range

    # Add contour regions (from most to least significant)
    # p < 0.01 (darkest)
    fig.add_trace(go.Scatter(
        x=np.concatenate([contour_01_lower, contour_01_upper[::-1]]),
        y=np.concatenate([se_range, se_range[::-1]]),
        fill='toself',
        fillcolor='rgba(220, 220, 255, 0.4)',
        line=dict(color='rgba(0, 0, 0, 0)'),
        name='p < 0.01',
        hoverinfo='skip',
        showlegend=True
    ))

    # 0.01 < p < 0.05
    fig.add_trace(go.Scatter(
        x=np.concatenate([contour_05_lower, contour_01_lower[::-1]]),
        y=np.concatenate([se_range, se_range[::-1]]),
        fill='toself',
        fillcolor='rgba(200, 200, 255, 0.3)',
        line=dict(color='rgba(0, 0, 0, 0)'),
        name='0.01 < p < 0.05',
        hoverinfo='skip',
        showlegend=True
    ))

    # Symmetric region on the other side
    fig.add_trace(go.Scatter(
        x=np.concatenate([contour_01_upper, contour_05_upper[::-1]]),
        y=np.concatenate([se_range, se_range[::-1]]),
        fill='toself',
        fillcolor='rgba(200, 200, 255, 0.3)',
        line=dict(color='rgba(0, 0, 0, 0)'),
        name='0.01 < p < 0.05',
        hoverinfo='skip',
        showlegend=False
    ))

    # 0.05 < p < 0.10
    fig.add_trace(go.Scatter(
        x=np.concatenate([contour_10_lower, contour_05_lower[::-1]]),
        y=np.concatenate([se_range, se_range[::-1]]),
        fill='toself',
        fillcolor='rgba(180, 180, 255, 0.2)',
        line=dict(color='rgba(0, 0, 0, 0)'),
        name='0.05 < p < 0.10',
        hoverinfo='skip',
        showlegend=True
    ))

    fig.add_trace(go.Scatter(
        x=np.concatenate([contour_05_upper, contour_10_upper[::-1]]),
        y=np.concatenate([se_range, se_range[::-1]]),
        fill='toself',
        fillcolor='rgba(180, 180, 255, 0.2)',
        line=dict(color='rgba(0, 0, 0, 0)'),
        name='0.05 < p < 0.10',
        hoverinfo='skip',
        showlegend=False
    ))

    # p > 0.10 (non-significant, white/no shading)

    # Pooled effect line
    fig.add_trace(go.Scatter(
        x=[pooled_effect, pooled_effect],
        y=[0, max(standard_errors) * 1.2],
        mode='lines',
        line=dict(color='red', dash='dash', width=2),
        name=f'Pooled: {pooled_effect:.3f}'
    ))

    # Calculate p-values for each study
    z_scores = effect_sizes / standard_errors
    p_values = 2 * (1 - stats.norm.cdf(np.abs(z_scores)))

    # Color studies by significance
    colors = []
    for p in p_values:
        if p < 0.01:
            colors.append('darkblue')
        elif p < 0.05:
            colors.append('blue')
        elif p < 0.10:
            colors.append('lightblue')
        else:
            colors.append('gray')

    # Add studies
    fig.add_trace(go.Scatter(
        x=effect_sizes,
        y=standard_errors,
        mode='markers',
        marker=dict(
            size=12,
            color=colors,
            line=dict(color='black', width=1),
            opacity=0.8
        ),
        text=[f"{name}<br>p = {p:.4f}" for name, p in zip(study_names, p_values)],
        hovertemplate='<b>%{text}</b><br>Effect: %{x:.3f}<br>SE: %{y:.3f}<extra></extra>',
        name='Studies'
    ))

    fig.update_layout(
        title=title,
        xaxis_title='Effect Size',
        yaxis_title='Standard Error',
        yaxis=dict(autorange='reversed'),
        hovermode='closest',
        template='plotly_white',
        height=700,
        legend=dict(x=0.02, y=0.98, bgcolor='rgba(255, 255, 255, 0.8)')
    )

    return fig


def trim_fill_funnel_plot(
    effect_sizes: np.ndarray,
    standard_errors: np.ndarray,
    filled_effect_sizes: np.ndarray,
    filled_standard_errors: np.ndarray,
    study_names: Optional[List[str]] = None,
    pooled_effect: Optional[float] = None,
    adjusted_effect: Optional[float] = None,
    title: str = "Trim-and-Fill Funnel Plot",
    interactive: bool = True
) -> go.Figure:
    """
    Funnel plot showing trim-and-fill results.

    Parameters:
        effect_sizes: Original effect sizes
        standard_errors: Original standard errors
        filled_effect_sizes: Effect sizes including imputed studies
        filled_standard_errors: Standard errors including imputed studies
        study_names: Study names
        pooled_effect: Original pooled effect
        adjusted_effect: Adjusted pooled effect after trim-and-fill
        title: Plot title
        interactive: Return interactive plot

    Returns:
        Plotly figure
    """
    n_original = len(effect_sizes)
    n_filled = len(filled_effect_sizes) - n_original

    if study_names is None:
        study_names = [f"Study {i+1}" for i in range(n_original)]

    fig = go.Figure()

    # Add confidence funnel for adjusted effect
    if adjusted_effect is not None:
        se_range = np.linspace(0, max(filled_standard_errors) * 1.1, 100)
        ci_lower = adjusted_effect - 1.96 * se_range
        ci_upper = adjusted_effect + 1.96 * se_range

        fig.add_trace(go.Scatter(
            x=np.concatenate([ci_lower, ci_upper[::-1]]),
            y=np.concatenate([se_range, se_range[::-1]]),
            fill='toself',
            fillcolor='rgba(128, 128, 128, 0.15)',
            line=dict(color='rgba(128, 128, 128, 0)'),
            name='95% CI (adjusted)',
            hoverinfo='skip'
        ))

        # Adjusted effect line
        fig.add_trace(go.Scatter(
            x=[adjusted_effect, adjusted_effect],
            y=[0, max(filled_standard_errors) * 1.1],
            mode='lines',
            line=dict(color='green', dash='dash', width=2),
            name=f'Adjusted: {adjusted_effect:.3f}'
        ))

    # Original pooled effect
    if pooled_effect is not None:
        fig.add_trace(go.Scatter(
            x=[pooled_effect, pooled_effect],
            y=[0, max(filled_standard_errors) * 1.1],
            mode='lines',
            line=dict(color='red', dash='dot', width=2),
            name=f'Original: {pooled_effect:.3f}'
        ))

    # Original studies
    fig.add_trace(go.Scatter(
        x=effect_sizes,
        y=standard_errors,
        mode='markers',
        marker=dict(size=12, color='blue', symbol='circle', opacity=0.7),
        text=study_names,
        hovertemplate='<b>%{text}</b><br>Effect: %{x:.3f}<br>SE: %{y:.3f}<extra></extra>',
        name='Observed Studies'
    ))

    # Filled (imputed) studies
    if n_filled > 0:
        filled_names = [f"Imputed {i+1}" for i in range(n_filled)]
        fig.add_trace(go.Scatter(
            x=filled_effect_sizes[n_original:],
            y=filled_standard_errors[n_original:],
            mode='markers',
            marker=dict(size=12, color='red', symbol='circle-open', opacity=0.7),
            text=filled_names,
            hovertemplate='<b>%{text}</b><br>Effect: %{x:.3f}<br>SE: %{y:.3f}<extra></extra>',
            name=f'Imputed Studies (n={n_filled})'
        ))

    fig.update_layout(
        title=title,
        xaxis_title='Effect Size',
        yaxis_title='Standard Error',
        yaxis=dict(autorange='reversed'),
        hovermode='closest',
        template='plotly_white',
        height=700
    )

    return fig


def comparison_funnel_plot(
    effect_sizes: np.ndarray,
    standard_errors: np.ndarray,
    methods_results: dict,
    study_names: Optional[List[str]] = None,
    title: str = "Multi-Method Comparison",
    interactive: bool = True
) -> go.Figure:
    """
    Compare multiple publication bias correction methods in one plot.

    Parameters:
        effect_sizes: Array of effect sizes
        standard_errors: Array of standard errors
        methods_results: Dictionary with method names as keys and effect estimates as values
        study_names: Study names
        title: Plot title
        interactive: Return interactive plot

    Returns:
        Plotly figure
    """
    if study_names is None:
        study_names = [f"Study {i+1}" for i in range(len(effect_sizes))]

    fig = go.Figure()

    # Add studies
    fig.add_trace(go.Scatter(
        x=effect_sizes,
        y=standard_errors,
        mode='markers',
        marker=dict(size=10, color='lightblue', opacity=0.6),
        text=study_names,
        hovertemplate='<b>%{text}</b><br>Effect: %{x:.3f}<br>SE: %{y:.3f}<extra></extra>',
        name='Studies'
    ))

    # Add method estimates as vertical lines
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
    for i, (method, estimate) in enumerate(methods_results.items()):
        color = colors[i % len(colors)]
        fig.add_trace(go.Scatter(
            x=[estimate, estimate],
            y=[0, max(standard_errors) * 1.1],
            mode='lines',
            line=dict(color=color, width=2, dash='dash'),
            name=f'{method}: {estimate:.3f}'
        ))

    fig.update_layout(
        title=title,
        xaxis_title='Effect Size',
        yaxis_title='Standard Error',
        yaxis=dict(autorange='reversed'),
        hovermode='closest',
        template='plotly_white',
        height=700,
        legend=dict(x=0.02, y=0.02)
    )

    return fig
