import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from .tracker import DB_PATH, CASINO_META

OUTPUT_PATH = Path(__file__).parent.parent / 'logs' / 'balance_chart.html'

_COLORS = {
    'stake_us':     '#1a9e5c',
    'fortune_wins': '#e74c3c',
    'acebet_cc':    '#2980b9',
}

# HTML page that wraps the plotly div.
# Placeholders use __UPPER__ style so normal CSS/JS braces need no escaping.
_PAGE = '''\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Bonus Harvest</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: #0c0c0c;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 48px 24px;
    }
    .wrap { width: 100%; max-width: 980px; }
    .hdr {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;
    }
    .brand {
      font-size: 10px;
      font-weight: 600;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      color: #2a2a2a;
    }
    .seg {
      display: inline-flex;
      background: #0f0f0f;
      border: 1px solid #1c1c1c;
      border-radius: 6px;
      padding: 2px;
      gap: 1px;
    }
    .seg button {
      background: transparent;
      border: none;
      color: #383838;
      font-family: inherit;
      font-size: 10px;
      font-weight: 600;
      letter-spacing: 0.08em;
      padding: 5px 18px;
      border-radius: 4px;
      cursor: pointer;
      transition: background 0.12s, color 0.12s;
    }
    .seg button:hover { color: #777; }
    .seg button.active { background: #1e1e1e; color: #bebebe; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hdr">
      <span class="brand">Bonus Harvest</span>
      <div class="seg" id="seg">
        <button class="active" onclick="setView('1W',this)">1W</button>
        <button onclick="setView('1M',this)">1M</button>
        <button onclick="setView('1Y',this)">1Y</button>
      </div>
    </div>
    <div id="chart">__PLOT__</div>
  </div>
  <script>
    const el = document.getElementById('chart').querySelector('.plotly-graph-div');
    const V = {
      '1W': { vis: __VIS_D__, range: ['__W_START__', '__END__'], fmt: '%b %d'  },
      '1M': { vis: __VIS_W__, range: ['__M_START__', '__END__'], fmt: '%b %d'  },
      '1Y': { vis: __VIS_M__, range: ['__Y_START__', '__END__'], fmt: '%b %Y' }
    };
    function setView(k, btn) {
      document.querySelectorAll('#seg button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const v = V[k];
      Plotly.update(el, {visible: v.vis}, {'xaxis.range': v.range, 'xaxis.tickformat': v.fmt});
    }
  </script>
</body>
</html>'''


def _load_raw() -> dict:
    """Return {casino: {day_to_balance, currency}} — last reading per calendar day."""
    conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
    rows = conn.execute('''
        SELECT DATE(recorded_at) AS day, casino, balance
        FROM balances b1
        WHERE balance IS NOT NULL
          AND recorded_at = (
              SELECT MAX(recorded_at) FROM balances b2
              WHERE b2.casino = b1.casino
                AND DATE(b2.recorded_at) = DATE(b1.recorded_at)
                AND b2.balance IS NOT NULL
          )
        ORDER BY day
    ''').fetchall()
    conn.close()

    raw: dict = {}
    for day, casino, balance in rows:
        if casino not in CASINO_META or CASINO_META[casino].get('disabled'):
            continue
        if casino not in raw:
            raw[casino] = {'day_to_balance': {}, 'currency': CASINO_META[casino]['currency']}
        raw[casino]['day_to_balance'][day] = round(balance, 2)
    return raw


def _aggregate(raw: dict, period: str) -> dict:
    """
    Bucket daily balances by 'day' | 'week' | 'month'.
    Each bucket holds the last known balance in that period.
    Week → Monday of that week. Month → 1st of that month.
    """
    result = {}
    for casino, data in raw.items():
        buckets: dict[str, float] = {}
        for day_str, balance in sorted(data['day_to_balance'].items()):
            dt = datetime.strptime(day_str, '%Y-%m-%d')
            if period == 'day':
                key = day_str
            elif period == 'week':
                key = (dt - timedelta(days=dt.weekday())).strftime('%Y-%m-%d')
            else:
                key = dt.strftime('%Y-%m-01')
            buckets[key] = balance
        result[casino] = {
            'dates':    sorted(buckets),
            'balances': [buckets[k] for k in sorted(buckets)],
            'currency': data['currency'],
        }
    return result


def generate_email_chart_b64() -> str:
    """
    Return a base64-encoded PNG of the all-time daily balance chart for embedding in email.
    Returns empty string if no data or matplotlib is unavailable.
    """
    try:
        import base64, io
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    except ImportError:
        return ''

    raw = _load_raw()
    if not raw:
        return ''

    daily_s  = _aggregate(raw, 'day')
    all_days = sorted({d for data in daily_s.values() for d in data['dates']})
    if not all_days:
        return ''

    dates = [datetime.strptime(d, '%Y-%m-%d') for d in all_days]

    fig, ax = plt.subplots(figsize=(7, 3), facecolor='#ffffff')
    ax.set_facecolor('#f9f9f9')

    bottom = [0.0] * len(all_days)
    for casino in raw:
        data    = daily_s.get(casino)
        if not data:
            continue
        meta    = CASINO_META[casino]
        color   = _COLORS.get(casino, '#aaaaaa')
        day_map = dict(zip(data['dates'], data['balances']))
        y_vals  = [day_map.get(d, 0.0) for d in all_days]
        ax.bar(dates, y_vals, bottom=bottom,
               label=f'{meta["display"]} ({data["currency"]})',
               color=color, width=0.55, zorder=2)
        bottom = [b + y for b, y in zip(bottom, y_vals)]

    ax.set_title('Balance History', fontsize=11, color='#1a1a2e', pad=8, fontweight='bold')
    ax.set_ylabel('Balance', fontsize=9, color='#666666')
    ax.tick_params(colors='#666666', labelsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:,.0f}'))
    ax.grid(axis='y', color='#e8e8e8', linewidth=0.6, zorder=1)
    for spine in ('top', 'right'):
        ax.spines[spine].set_visible(False)
    for spine in ('left', 'bottom'):
        ax.spines[spine].set_color('#e0e0e0')
    ax.legend(fontsize=8, framealpha=0, loc='upper left')
    plt.tight_layout(pad=0.8)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, facecolor='#ffffff')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def generate_chart(output_path: Path | None = None) -> Path:
    """
    Generate a polished stacked-bar HTML chart.
    1W = daily bars (last 7 days)
    1M = weekly bars (last 5 weeks)
    1Y = monthly bars (last 12 months)
    """
    try:
        import plotly.graph_objects as go
    except ImportError:
        raise ImportError('plotly is required — pip install plotly')

    out = Path(output_path) if output_path else OUTPUT_PATH
    out.parent.mkdir(exist_ok=True)

    raw = _load_raw()
    if not raw:
        out.write_text('<html><body style="background:#0c0c0c;color:#333;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;"><p>No balance data yet.</p></body></html>')
        return out

    casinos  = list(raw.keys())
    n        = len(casinos)
    daily_s  = _aggregate(raw, 'day')
    weekly_s = _aggregate(raw, 'week')
    monthly_s = _aggregate(raw, 'month')

    def make_bars(agg: dict, visible: bool) -> list:
        all_days = sorted({d for data in agg.values() for d in data['dates']})
        bars = []
        for casino in casinos:
            data     = agg.get(casino, {'dates': [], 'balances': [], 'currency': raw[casino]['currency']})
            meta     = CASINO_META[casino]
            color    = _COLORS.get(casino, '#aaaaaa')
            currency = data['currency']
            day_map  = dict(zip(data['dates'], data['balances']))
            y_vals   = [day_map.get(d, 0.0) for d in all_days]
            bars.append(go.Bar(
                x=all_days,
                y=y_vals,
                name=f'{meta["display"]} ({currency})',
                marker_color=color,
                marker_line_width=0,
                visible=visible,
                showlegend=True,
                hoverinfo='skip',
            ))
        return bars

    # Three groups: daily (1W), weekly (1M), monthly (1Y) — one group visible at a time
    traces = (
        make_bars(daily_s,   visible=True)  +
        make_bars(weekly_s,  visible=False) +
        make_bars(monthly_s, visible=False)
    )

    all_days_flat = sorted(d for c in casinos for d in raw[c]['day_to_balance'])
    latest_dt     = datetime.strptime(max(all_days_flat), '%Y-%m-%d')
    end           = (latest_dt + timedelta(days=2)).strftime('%Y-%m-%d')
    w_start       = (latest_dt - timedelta(days=6)).strftime('%Y-%m-%d')
    m_start       = (latest_dt - timedelta(days=34)).strftime('%Y-%m-%d')
    y_start       = (latest_dt - timedelta(days=364)).strftime('%Y-%m-%d')

    vis_d = str([True]*n  + [False]*n + [False]*n).lower()
    vis_w = str([False]*n + [True]*n  + [False]*n).lower()
    vis_m = str([False]*n + [False]*n + [True]*n ).lower()

    fig = go.Figure(data=traces)
    fig.update_layout(
        barmode='stack',
        bargap=0.4,
        paper_bgcolor='#0c0c0c',
        plot_bgcolor='#0c0c0c',
        font=dict(
            family='-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif',
            color='#3a3a3a',
            size=10,
        ),
        xaxis=dict(
            type='date',
            showgrid=False,
            showline=False,
            tickformat='%b %d',
            ticklen=0,
            range=[w_start, end],
            rangeslider=dict(visible=False),
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#161616',
            gridwidth=1,
            showline=False,
            ticklen=0,
            zeroline=False,
            tickformat=',.0f',
            nticks=5,
        ),
        hovermode=False,
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.14,
            xanchor='left',
            x=0,
            font=dict(size=10, color='#3a3a3a'),
            bgcolor='rgba(0,0,0,0)',
            borderwidth=0,
            itemsizing='constant',
        ),
        margin=dict(t=16, b=80, l=52, r=12),
        height=400,
    )

    plot_div = fig.to_html(
        full_html=False,
        include_plotlyjs='cdn',
        config={'displayModeBar': False, 'responsive': True},
    )

    html = (_PAGE
        .replace('__PLOT__',    plot_div)
        .replace('__VIS_D__',   vis_d)
        .replace('__VIS_W__',   vis_w)
        .replace('__VIS_M__',   vis_m)
        .replace('__W_START__', w_start)
        .replace('__M_START__', m_start)
        .replace('__Y_START__', y_start)
        .replace('__END__',     end)
    )
    out.write_text(html)
    return out
