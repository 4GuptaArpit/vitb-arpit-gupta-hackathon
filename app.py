"""
RiskPulse AI - Unified Financial Risk Intelligence Platform
Interactive Command Center for S&P Global x CRISIL Campus Hackathon 2026

Candidate: Arpit Gupta
College: Vellore Institute of Technology, Bhopal
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.engine import IngestionPipeline, RiskEngine, RiskSignal
from src.modules import TacticalIndexRebalancer, StressTester, INDEX_BASKET

# Page Configuration - Institutional Dark/Clean Layout
st.set_page_config(
    page_title="RiskPulse AI | S&P Global x CRISIL Hackathon",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Professional Financial Terminal Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #0e1117;
        border: 1px solid #262730;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge-pos { color: #00cc96; font-weight: 600; }
    .badge-neg { color: #ef553b; font-weight: 600; }
    .badge-neu { color: #ab63fa; font-weight: 600; }
    .stTabs [data-baseweb="tab-list"] { gap: 16px; }
    .stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: 600; padding: 10px 20px; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_core_systems():
    """Initializes and caches core NLP engine and downstream modules."""
    pipeline = IngestionPipeline()
    engine = RiskEngine()
    rebalancer = TacticalIndexRebalancer()
    stress_tester = StressTester()
    stream = pipeline.run()
    signals = engine.process_stream(stream)
    return engine, pipeline, rebalancer, stress_tester, signals


engine, pipeline, rebalancer, stress_tester, signals = load_core_systems()

# Top Header Bar
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("⚡ RiskPulse AI — Financial Risk Intelligence Platform")
    st.caption("S&P Global × CRISIL Campus Hackathon 2026 | Candidate: Arpit Gupta (VIT Bhopal)")
with col_h2:
    st.write("")
    if st.button("🔄 Reload Live Feeds", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()

# Global KPI Metric Ribbon
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
total_sigs = len(signals)
avg_sent = np.mean([s.sentiment_score for s in signals])
high_impact = len([s for s in signals if s.impact_score >= 7])
neg_sigs = len([s for s in signals if s.sentiment_score < -0.15])
pos_sigs = len([s for s in signals if s.sentiment_score > 0.15])

kpi1.metric("Ingested Signals", f"{total_sigs} Feeds")
kpi2.metric("Mean Market Sentiment", f"{avg_sent:+.2f}", delta=f"{avg_sent:+.2f}")
kpi3.metric("High-Impact Alerts (≥7)", f"{high_impact}", delta="Elevated Risk", delta_color="inverse")
kpi4.metric("Negative Signals", f"{neg_sigs}", delta="-Bearish", delta_color="inverse")
kpi5.metric("Positive Signals", f"{pos_sigs}", delta="+Bullish")

st.markdown("---")

# Main Navigation Tabs
tab_feed, tab_mod_a, tab_mod_b, tab_adhoc, tab_arch = st.tabs([
    "📡 NLP Risk Signal Feed",
    "📊 Module A: Index Rebalancer",
    "🏦 Module B: Portfolio Stress Tester",
    "🧪 Ad-Hoc Live Signal Tester",
    "🏛️ Architecture & Methodology"
])

# ==========================================
# TAB 1: NLP RISK SIGNAL FEED
# ==========================================
with tab_feed:
    st.subheader("Real-Time Multi-Source Risk Signal Stream")
    st.write("Processed from financial news headlines (Reuters/Bloomberg) and market social feeds.")

    filter_c1, filter_c2, filter_c3 = st.columns([1, 1, 1])
    with filter_c1:
        cat_filter = st.selectbox(
            "Filter Event Type:",
            ["All"] + sorted(list(set(s.event_classification for s in signals)))
        )
    with filter_c2:
        src_filter = st.selectbox("Filter Source:", ["All", "News", "Social"])
    with filter_c3:
        min_impact_filter = st.slider("Min Impact Severity:", 1, 10, 1)

    filtered = signals
    if cat_filter != "All":
        filtered = [s for s in filtered if s.event_classification == cat_filter]
    if src_filter != "All":
        filtered = [s for s in filtered if s.source_type.startswith(src_filter.lower())]
    filtered = [s for s in filtered if s.impact_score >= min_impact_filter]

    # Visual Analytics Ribbon
    chart_c1, chart_c2 = st.columns(2)
    with chart_c1:
        event_counts = pd.DataFrame([s.event_classification for s in filtered], columns=["Event"]).value_counts().reset_index()
        event_counts.columns = ["Event", "Count"]
        fig_events = px.bar(
            event_counts, x="Event", y="Count", color="Event",
            title="Event Category Distribution",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig_events.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
        st.plotly_chart(fig_events, use_container_width=True)

    with chart_c2:
        sent_df = pd.DataFrame([{"Sentiment": s.sentiment_score, "Impact": s.impact_score, "Ticker": s.ticker} for s in filtered])
        fig_scatter = px.scatter(
            sent_df, x="Sentiment", y="Impact", color="Sentiment",
            title="Sentiment Score vs. Impact Severity",
            color_continuous_scale="RdYlGn", hover_data=["Ticker"],
            range_x=[-1.0, 1.0], range_y=[0.5, 10.5]
        )
        fig_scatter.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Detailed Signal Table
    table_data = []
    for s in filtered[:50]:
        table_data.append({
            "Source": s.publisher,
            "Ticker": s.ticker,
            "Event": s.event_classification,
            "Sentiment": f"{s.sentiment_score:+.2f} ({s.sentiment_label})",
            "Impact": f"{s.impact_score}/10",
            "Confidence": f"{int(s.confidence_score * 100)}%",
            "Headline / Narrative": s.headline,
            "Key Drivers": ", ".join(s.key_drivers) if s.key_drivers else "N/A"
        })

    st.dataframe(pd.DataFrame(table_data), use_container_width=True, height=400)

# ==========================================
# TAB 2: MODULE A - TACTICAL INDEX REBALANCER
# ==========================================
with tab_mod_a:
    st.subheader("Module A: Tactical High-Frequency Stock Index Rebalancer")
    st.write("Dynamic sentiment-driven rebalancing of 20 S&P 100 constituent stocks with institutional concentration constraints.")

    st_col1, st_col2 = st.columns([1, 2])
    with st_col1:
        st.markdown("### Execution Controls")
        alpha_val = st.slider("Sensitivity Alpha (α):", 0.10, 0.80, 0.35, 0.05,
                              help="Controls how aggressively sentiment moves portfolio weights")
        rebalancer.sensitivity_alpha = alpha_val

        if st.button("🚀 Run Sequential Rebalancing Simulation", use_container_width=True):
            rebalancer.rebalance_batch(signals)
            st.success("Rebalanced index across active signal feed!")

        if st.button("↩️ Reset to Benchmark Weights", use_container_width=True):
            rebalancer.__init__(sensitivity_alpha=alpha_val)
            st.info("Reset to benchmark weights.")

        st.markdown("---")
        st.markdown("#### Institutional Guardrails")
        st.write("• **Sum of Weights:** Strictly normalized to 100.0%")
        st.write("• **Floor Weight:** 1.0% (Diversification guarantee)")
        st.write("• **Ceiling Weight:** 18.0% (Single-asset concentration cap)")

    with st_col2:
        state_df = rebalancer.get_current_state()

        fig_treemap = px.treemap(
            state_df,
            path=["sector", "ticker"],
            values="current_weight",
            color="weight_drift_pct",
            color_continuous_scale="RdYlGn",
            color_continuous_midpoint=0.0,
            title="Index Weight Allocation & Sentiment Drift (%)"
        )
        fig_treemap.update_layout(height=420, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_treemap, use_container_width=True)

    st.markdown("### Constituent Drift & Execution History")
    col_w1, col_w2 = st.columns([3, 2])
    with col_w1:
        fig_drift = px.bar(
            state_df.sort_values(by="weight_drift_pct", ascending=False),
            x="ticker", y="weight_drift_pct",
            color="weight_drift_pct",
            color_continuous_scale="RdYlGn",
            title="Weight Drift vs. Benchmark (%)"
        )
        fig_drift.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_drift, use_container_width=True)

    with col_w2:
        st.markdown("#### Recent Rebalance Events")
        if rebalancer.rebalance_history:
            hist_df = pd.DataFrame([e.to_dict() for e in reversed(rebalancer.rebalance_history[-8:])])
            st.dataframe(hist_df[["ticker_affected", "sentiment_label", "weight_before_pct", "weight_after_pct", "delta_pct"]],
                         use_container_width=True, height=270)
        else:
            st.info("Click 'Run Sequential Rebalancing Simulation' above to generate execution logs.")

# ==========================================
# TAB 3: MODULE B - PORTFOLIO STRESS TESTER
# ==========================================
with tab_mod_b:
    st.subheader("Module B: Strategic Portfolio Stress-Testing Tool")
    st.write("Simulates multi-factor macroeconomic and credit shocks on a $1.10B synthetic wholesale banking portfolio.")

    stress_ctrl1, stress_ctrl2, stress_ctrl3 = st.columns([1, 1, 1])
    with stress_ctrl1:
        event_choice = st.selectbox(
            "Trigger Event Type:",
            ["Geopolitical", "Credit Event", "Macroeconomic", "Regulatory", "Merger/Acquisition", "Product Launch"]
        )
    with stress_ctrl2:
        impact_choice = st.slider("Event Impact Severity Score (1-10):", 1, 10, 8)
    with stress_ctrl3:
        sector_target = st.selectbox(
            "Sector Vulnerability Shock:",
            ["None", "Energy", "Financial Services", "Semiconductors", "Telecommunications", "Automotive", "Healthcare"]
        )

    # Execute Stress Test
    target_sec = None if sector_target == "None" else sector_target
    stress_result = stress_tester.run_stress_test(
        event_type=event_choice,
        impact_score=impact_choice,
        target_sector=target_sec
    )

    # Results KPI Ribbon
    res_kpi1, res_kpi2, res_kpi3, res_kpi4 = st.columns(4)
    res_kpi1.metric("Pre-Stress Baseline", f"${stress_result.baseline_value_usd/1e6:.2f}M")
    res_kpi2.metric(
        "Post-Stress Mark-to-Market",
        f"${stress_result.stressed_value_usd/1e6:.2f}M",
        delta=f"${stress_result.total_pnl_usd/1e6:.2f}M ({stress_result.pnl_percentage:.2f}%)",
        delta_color="inverse"
    )
    res_kpi3.metric(
        "Expected Loss Surge (EL)",
        f"${stress_result.stressed_expected_loss_usd/1e6:.2f}M",
        delta=f"+${stress_result.el_increase_usd/1e6:.2f}M",
        delta_color="inverse"
    )
    res_kpi4.metric(
        "99% Value-at-Risk (VaR)",
        f"${stress_result.var_99_stressed_usd/1e6:.2f}M",
        delta=f"+${(stress_result.var_99_stressed_usd - stress_result.var_99_baseline_usd)/1e6:.2f}M",
        delta_color="inverse"
    )

    st.markdown("---")

    # Breakdown Visualizations
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        st.markdown("#### Asset Class Vulnerability Breakdown")
        breakdown_df = pd.DataFrame(stress_result.asset_breakdown)
        fig_bar = px.bar(
            breakdown_df, x="asset_type", y=["baseline_mv_usd", "stressed_mv_usd"],
            barmode="group",
            title="Portfolio Value Pre vs. Post Stress ($ USD)",
            labels={"value": "Market Value ($)", "asset_type": "Asset Class"},
            color_discrete_map={"baseline_mv_usd": "#636efa", "stressed_mv_usd": "#ef553b"}
        )
        fig_bar.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    with b_col2:
        st.markdown("#### P&L Impact by Asset Class (%)")
        fig_loss = px.bar(
            breakdown_df, x="asset_type", y="pnl_pct",
            color="pnl_pct",
            color_continuous_scale="Reds_r",
            title="Percentage Drawdown per Asset Class (%)",
            labels={"pnl_pct": "P&L Drawdown (%)", "asset_type": "Asset Class"}
        )
        fig_loss.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_loss, use_container_width=True)

    st.markdown("#### Detailed Wholesale Portfolio Stress Exposure Table")
    if stress_result.stressed_positions_df is not None:
        st.dataframe(stress_result.stressed_positions_df[[
            "position_id", "asset_type", "counterparty", "sector", "notional_usd",
            "credit_rating", "tenor_years", "current_mv_usd", "stressed_mv_usd", "pnl_usd", "pnl_pct"
        ]], use_container_width=True, height=320)

# ==========================================
# TAB 4: AD-HOC LIVE SIGNAL TESTER
# ==========================================
with tab_adhoc:
    st.subheader("🧪 Live Ad-Hoc NLP Signal Analysis")
    st.write("Type or paste any financial headline, earnings snippet, or news alert to run live risk scoring.")

    test_input = st.text_area(
        "Financial Text Input:",
        value="Moody's places senior unsecured notes on downgrade review due to ballooning debt maturities and liquidity crunch.",
        height=100
    )
    t_c1, t_c2 = st.columns([1, 2])
    with t_c1:
        test_ticker = st.text_input("Company Ticker (optional):", value="XYZ")
        test_engagement = st.slider("Engagement / Virality Proxy:", 0, 500, 150)
        analyze_btn = st.button("⚡ Score Risk Signal", use_container_width=True)

    if analyze_btn or test_input:
        res_sig = engine.process_item({
            "id": "adhoc_demo",
            "ticker": test_ticker.upper() if test_ticker else "GENERAL",
            "source_type": "adhoc_tester",
            "publisher": "Live Demo User",
            "timestamp": "Now",
            "headline": test_input[:80],
            "text": test_input,
            "engagement_score": test_engagement
        })

        with t_c2:
            st.markdown("### Structured Output Signal")
            out_c1, out_c2, out_c3 = st.columns(3)
            out_c1.metric("Sentiment Score", f"{res_sig.sentiment_score:+.2f}", res_sig.sentiment_label)
            out_c2.metric("Event Category", res_sig.event_classification, f"{int(res_sig.confidence_score*100)}% Conf.")
            out_c3.metric("Impact Severity", f"{res_sig.impact_score}/10", "High Risk" if res_sig.impact_score >= 7 else "Moderate")

            st.json(res_sig.to_dict())

# ==========================================
# TAB 5: ARCHITECTURE & METHODOLOGY
# ==========================================
with tab_arch:
    st.subheader("🏛️ Architecture, Tech Stack & Methodology")
    st.markdown("""
    ### System Design
    ```
    [Multi-Source Ingestion: News & Social]
                    │
                    ▼
    [AI/NLP Risk Engine: FinBERT + Domain Lexicon + Zero-Shot Classifier]
                    │
                    ▼
         [Structured RiskSignal Bus]
          ├── Sentiment Score: [-1.0 to +1.0]
          ├── Event Classification: [6 Institutional Categories]
          └── Impact Score: [1 to 10 Severity]
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
    [Module A: Tactical Rebalancer]   [Module B: Wholesale Stress Tester]
    • S&P 100 20-Stock Basket         • $1.10B Multi-Asset Wholesale Book
    • Sentiment Alpha Scaling         • Spread Widening & PD Multipliers
    • Diversification Bounds [1%-18%] • Expected Loss (EL) & 99% VaR Shifts
    ```

    ### Key Methodology Highlights
    1. **Domain Understanding:** Incorporates CRISIL/Basel credit risk formulations ($EL = EAD \times PD \times LGD$), spread widening shocks, and modified duration MTM impacts.
    2. **Institutional Guardrails:** Prevents portfolio blowout by clamping weights and normalizing $\sum w_i = 100.0\%$.
    3. **Sub-second Inference:** Hybrid FinBERT and rule-based ensemble guarantees deterministic, reproducible demonstration without API limits or offline failures.
    """)
