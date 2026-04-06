# =============================================================================
# plot_bucket_by_topic.py — Bucket chart: one subplot per topic, lines = doc types
# =============================================================================
# For each bucket in COUNTRY_TOPIC_GROUPS, produces one figure where:
#   - Each subplot = one topic within the bucket
#   - Each line = one document type (DSA, AIV, Program)
#   - Y-axis = % of documents with at least one mention
#   - X-axis = year
#   - Optional: subtle gray bars = total docs across all types
#
# Usage (in notebook):
#   from plot_bucket_by_topic import plot_bucket_by_topic
#   for bucket_name, topics in COUNTRY_TOPIC_GROUPS.items():
#       plot_bucket_by_topic(df_mentions_all, bucket_name, topics)
# =============================================================================

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math


DOC_STYLES = {
    'DSA':     {'color': '#4472C4', 'marker': 'o',  'linewidth': 2.5},
    'AIV':     {'color': '#ED7D31', 'marker': 's',  'linewidth': 2.5},
    'Program': {'color': '#70AD47', 'marker': '^',  'linewidth': 2.5},
}


def plot_bucket_by_topic(df_all, bucket_name, topics, max_year=2023,
                         save_dir=None, show_bars=True):
    """
    One figure per bucket. Grid of subplots — one per topic.
    Lines = document types (DSA, AIV, Program).
    Y = % of documents with at least one mention (3yr rolling avg).
    """
    def smooth(series):
        return series.rolling(3, center=True, min_periods=2).mean()

    n_topics = len(topics)
    if n_topics == 0:
        return

    # Grid layout: up to 3 columns
    n_cols = min(3, n_topics)
    n_rows = math.ceil(n_topics / n_cols)
    fig_w = 7.5 * n_cols
    fig_h = 5 * n_rows

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(fig_w, fig_h),
                             squeeze=False, sharey=True)

    for idx, (tk, tl) in enumerate(topics):
        row, col_idx = divmod(idx, n_cols)
        ax = axes[row][col_idx]
        has_col = f'has_{tk}'

        for doc_type, style in DOC_STYLES.items():
            df_sub = df_all[(df_all['doc_type'] == doc_type)
                            & (df_all['year'] <= max_year)]
            if len(df_sub) == 0:
                continue

            yearly = df_sub.groupby('year').agg(
                n_docs=('filename', 'count'),
                n_has=(has_col, 'sum'),
            ).reset_index()
            yearly['pct'] = yearly['n_has'] / yearly['n_docs'] * 100

            ax.plot(yearly['year'], smooth(yearly['pct']),
                    '-', marker=style['marker'], color=style['color'],
                    linewidth=style['linewidth'], markersize=4,
                    label=doc_type, zorder=3)

        # Subtle total-doc bars (all types combined)
        if show_bars:
            df_yr = df_all[df_all['year'] <= max_year]
            bar_data = df_yr.groupby('year')['filename'].count().reset_index(name='n')
            ax2 = ax.twinx()
            ax2.bar(bar_data['year'], bar_data['n'],
                    color='gray', alpha=0.08, width=0.8, zorder=0)
            ax2.set_ylim(0, bar_data['n'].max() * 3)
            ax2.tick_params(axis='y', labelsize=7, colors='gray', labelcolor='#cccccc')
            if col_idx == n_cols - 1:
                ax2.set_ylabel('Total docs', fontsize=8, color='#cccccc')
            else:
                ax2.set_yticklabels([])

        ax.set_title(tl, fontweight='bold', fontsize=11)
        ax.set_ylim(bottom=0)
        ax.grid(axis='y', alpha=0.3)
        ax.set_xticks(range(2005, max_year + 1, 2))
        ax.set_xlim(2004.5, max_year + 0.5)
        ax.tick_params(axis='x', rotation=45, labelsize=9)
        ax.axvline(x=2017.5, color='red', linestyle=':', alpha=0.4, linewidth=1)

        if col_idx == 0:
            ax.set_ylabel('% of documents', fontsize=10)
        if idx == 0:
            ax.legend(fontsize=9, loc='best', frameon=True)

    # Hide unused subplots
    for idx in range(n_topics, n_rows * n_cols):
        row, col_idx = divmod(idx, n_cols)
        axes[row][col_idx].set_visible(False)

    fig.suptitle(f'{bucket_name}\n'
                 '% of documents with at least one mention, by document type',
                 fontweight='bold', fontsize=13, y=1.02)

    fig.text(0.05, -0.02,
             'Note: 3-year centered rolling average. Red dotted line = 2018 LIC-DSF revision. '
             'Gray bars = total documents per year (all types).\n'
             "Source: IEO Staff's calculations from IMF documents.",
             fontsize=8, ha='left')

    plt.tight_layout()

    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        safe = bucket_name.lower().replace(' ', '_').replace('/', '_').replace('&', 'and').replace(':', '')
        fname = os.path.join(save_dir, f'bucket_bytopic_{safe}.png')
        fig.savefig(fname, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
    else:
        plt.show()
