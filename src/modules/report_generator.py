"""
Executive PDF Risk Report Generator for Wholesale Portfolio Stress Tests.
Generates an institutional audit-ready PDF risk memorandum for credit committees.
"""

from pathlib import Path
from typing import Any, Dict, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from .stress_tester import StressTestResult


def generate_stress_report(result: StressTestResult, output_path: str = "stress_test_report.pdf") -> str:
    """Compiles an institutional CRISIL-grade PDF risk memorandum with pixel-perfect table layouts."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        title=f"CRISIL Executive Stress Test Memorandum - {result.event_type.upper()}",
        author="RiskPulse AI | S&P Global x CRISIL Hackathon 2026",
        subject=f"Capital Adequacy & Wholesale Stress Test ({result.event_type})",
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    NAVY = colors.HexColor("#0f172a")
    SLATE = colors.HexColor("#1e293b")
    ROSE = colors.HexColor("#ef4444")
    SKY = colors.HexColor("#0284c7")

    title_style = ParagraphStyle(
        'RepTitle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=NAVY, spaceAfter=4
    )
    sub_style = ParagraphStyle(
        'RepSub', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=SKY, spaceAfter=14
    )
    body_style = ParagraphStyle(
        'RepBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor("#334155")
    )
    bold_style = ParagraphStyle(
        'RepBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9.5, leading=14, textColor=NAVY
    )
    th_style = ParagraphStyle(
        'RepTH', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.white
    )
    cell_style = ParagraphStyle(
        'RepCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=11, textColor=colors.HexColor("#334155")
    )
    cell_rose_bold = ParagraphStyle(
        'RepCellRose', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=ROSE
    )

    elements = []

    # Title & Header
    elements.append(Paragraph("RISKPULSE AI &mdash; EXECUTIVE STRESS TEST MEMORANDUM", title_style))
    elements.append(Paragraph(f"S&amp;P GLOBAL &times; CRISIL HACKATHON 2026 | SCENARIO: {result.event_type.upper()} (SEVERITY: {result.impact_score}/10)", sub_style))
    elements.append(Spacer(1, 4))

    # Executive Summary Box
    summary_text = (
        f"This memorandum presents the simulated impact of a high-severity {result.event_type} event "
        f"(calibrated severity score of {result.impact_score}/10) on the institutional wholesale banking portfolio ($1.10B baseline notional). "
        f"Multi-factor shocks were applied across credit spread widening, rating migration PD multipliers, and duration-adjusted mark-to-market prices."
    )
    elements.append(Paragraph(summary_text, body_style))
    elements.append(Spacer(1, 12))

    # Key Metrics Table
    elements.append(Paragraph("<b>1. Summary Impact Metrics</b>", bold_style))
    elements.append(Spacer(1, 4))

    metrics_data = [
        [
            Paragraph("<b>Metric</b>", th_style),
            Paragraph("<b>Pre-Stress Baseline</b>", th_style),
            Paragraph("<b>Post-Stress Stressed</b>", th_style),
            Paragraph("<b>Net Variance / Impact</b>", th_style)
        ],
        [
            Paragraph("Portfolio Market Value", cell_style),
            Paragraph(f"${result.baseline_value_usd/1e6:,.2f}M", cell_style),
            Paragraph(f"${result.stressed_value_usd/1e6:,.2f}M", cell_style),
            Paragraph(f"${result.total_pnl_usd/1e6:,.2f}M ({result.pnl_percentage:.2f}%)", cell_rose_bold)
        ],
        [
            Paragraph("Expected Loss (EL = EAD*PD*LGD)", cell_style),
            Paragraph(f"${result.baseline_expected_loss_usd/1e6:,.2f}M", cell_style),
            Paragraph(f"${result.stressed_expected_loss_usd/1e6:,.2f}M", cell_style),
            Paragraph(f"+${result.el_increase_usd/1e6:,.2f}M", cell_rose_bold)
        ],
        [
            Paragraph("99% Value-at-Risk (VaR)", cell_style),
            Paragraph(f"${result.var_99_baseline_usd/1e6:,.2f}M", cell_style),
            Paragraph(f"${result.var_99_stressed_usd/1e6:,.2f}M", cell_style),
            Paragraph(f"+${(result.var_99_stressed_usd - result.var_99_baseline_usd)/1e6:,.2f}M", cell_rose_bold)
        ]
    ]
    # Printable width: 612 - 80 = 532. [180, 110, 110, 132] = 532 exact!
    t_metrics = Table(metrics_data, colWidths=[180, 110, 110, 132])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_metrics)
    elements.append(Spacer(1, 14))

    # Asset Class Breakdown Table
    elements.append(Paragraph("<b>2. Asset Class Drawdown Breakdown</b>", bold_style))
    elements.append(Spacer(1, 4))

    asset_headers = [
        Paragraph("<b>Asset Class</b>", th_style),
        Paragraph("<b>Positions</b>", th_style),
        Paragraph("<b>Baseline ($M)</b>", th_style),
        Paragraph("<b>Stressed ($M)</b>", th_style),
        Paragraph("<b>Drawdown ($M)</b>", th_style),
        Paragraph("<b>Loss (%)</b>", th_style)
    ]
    asset_rows = [asset_headers]
    for b in result.asset_breakdown:
        asset_rows.append([
            Paragraph(b["asset_type"], cell_style),
            Paragraph(str(b["positions_count"]), cell_style),
            Paragraph(f"${b['baseline_mv_usd']/1e6:,.2f}M", cell_style),
            Paragraph(f"${b['stressed_mv_usd']/1e6:,.2f}M", cell_style),
            Paragraph(f"${b['pnl_usd']/1e6:,.2f}M", cell_rose_bold),
            Paragraph(f"{b['pnl_pct']:.2f}%", cell_rose_bold)
        ])
    # Printable width: 532. [142, 65, 80, 80, 85, 80] = 532 exact!
    t_assets = Table(asset_rows, colWidths=[142, 65, 80, 80, 85, 80])
    t_assets.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SLATE),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_assets)
    elements.append(Spacer(1, 16))

    # Committee Recommendation Footer
    elements.append(Paragraph("<b>3. Risk Committee Next Actions</b>", bold_style))
    elements.append(Spacer(1, 4))
    recs = [
        "&bull; Active hedging via interest rate swaps to offset duration MTM drag.",
        "&bull; Review collateral hair-cuts and credit limits on high-yield debt counterparties.",
        "&bull; Reallocate derivative protections to curtail CDS mark-to-market exposure."
    ]
    for r in recs:
        elements.append(Paragraph(r, body_style))

    doc.build(elements)
    return str(Path(output_path).resolve())


def generate_signal_alert_report(
    headline: str,
    ticker: str,
    event_type: str,
    sentiment_score: float,
    impact_score: float,
    publisher: str = "Market News Wire",
    key_drivers: Optional[list] = None,
    output_path: str = "event_credit_alert.pdf"
) -> str:
    """Compiles an institutional 1-page CRISIL Credit Risk & Market Watch memorandum."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        title=f"CRISIL Credit Watch Alert - {ticker}",
        author="RiskPulse AI | S&P Global x CRISIL Hackathon 2026",
        subject=f"Event Risk Assessment for {ticker}",
        leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40
    )
    styles = getSampleStyleSheet()
    NAVY = colors.HexColor("#0f172a")
    ROSE = colors.HexColor("#ef4444")
    EMERALD = colors.HexColor("#10b981")
    SKY = colors.HexColor("#0284c7")

    title_style = ParagraphStyle(
        'AlertTitle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=17, leading=21, textColor=NAVY, spaceAfter=4
    )
    sub_style = ParagraphStyle(
        'AlertSub', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=SKY, spaceAfter=10
    )
    body_style = ParagraphStyle(
        'AlertBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor("#334155")
    )
    bold_style = ParagraphStyle(
        'AlertBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9.5, leading=14, textColor=NAVY
    )
    table_cell_style = ParagraphStyle(
        'AlertTableCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=11, textColor=colors.HexColor("#334155")
    )
    table_cell_bold = ParagraphStyle(
        'AlertTableCellBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=11,
        textColor=ROSE if sentiment_score < 0 else EMERALD
    )

    elements = []
    elements.append(Paragraph("CRISIL / S&amp;P GLOBAL &mdash; EVENT RISK &amp; CREDIT WATCH ALERT", title_style))
    elements.append(Paragraph(f"TICKER: {ticker} | EVENT: {event_type.upper()} | PUBLISHER: {publisher}", sub_style))
    elements.append(Spacer(1, 4))

    elements.append(Paragraph("<b>1. Event Intelligence &amp; Narrative Summary</b>", bold_style))
    elements.append(Spacer(1, 3))
    clean_headline = headline.replace('"', '&quot;')
    elements.append(Paragraph(f"<b>Headline:</b> <i>&ldquo;{clean_headline}&rdquo;</i>", body_style))
    elements.append(Spacer(1, 3))
    elements.append(Paragraph(
        f"The RiskPulse AI NLP Risk Engine has classified this market development under the <b>{event_type}</b> "
        f"pillar with a calibrated sentiment polarity of <b>{sentiment_score:+.2f}</b> and systemic severity of <b>{impact_score}/10</b>. "
        f"This alert summarizes expected asset allocation drift and credit transmission channels.", body_style
    ))
    elements.append(Spacer(1, 8))

    # Analytical metrics table
    elements.append(Paragraph("<b>2. Quantitative Transmission &amp; Impact Projections</b>", bold_style))
    elements.append(Spacer(1, 3))

    est_delta = sentiment_score * (impact_score / 10.0) * 1.2
    spread_bps = round(abs(sentiment_score) * impact_score * 8.5)
    pd_mult = 1.0 + (max(0.0, -sentiment_score) * (impact_score / 10.0) * 1.5)

    metrics_data = [
        [
            Paragraph("<b>Dimension</b>", ParagraphStyle('TH', parent=styles['Normal'], textColor=colors.white, fontName='Helvetica-Bold', fontSize=8.5)),
            Paragraph("<b>Model Metric</b>", ParagraphStyle('TH', parent=styles['Normal'], textColor=colors.white, fontName='Helvetica-Bold', fontSize=8.5)),
            Paragraph("<b>Projected Transmission Impact</b>", ParagraphStyle('TH', parent=styles['Normal'], textColor=colors.white, fontName='Helvetica-Bold', fontSize=8.5))
        ],
        [
            Paragraph("FinBERT Sentiment Polarity", table_cell_style),
            Paragraph(f"{sentiment_score:+.2f}", table_cell_bold),
            Paragraph("Negative / Bearish Drag" if sentiment_score < 0 else "Positive / Expansionary", table_cell_style)
        ],
        [
            Paragraph("Systemic Impact Severity", table_cell_style),
            Paragraph(f"{impact_score}/10", table_cell_bold),
            Paragraph("High Market Impact" if impact_score >= 6 else "Moderate Impact", table_cell_style)
        ],
        [
            Paragraph("Module A Index Weight Drift", table_cell_style),
            Paragraph(f"{est_delta:+.2f}%", table_cell_bold),
            Paragraph("Capital reallocated to non-correlated constituents", table_cell_style)
        ],
        [
            Paragraph("Module B Credit Spread Widening", table_cell_style),
            Paragraph(f"+{spread_bps} bps", table_cell_bold),
            Paragraph("Secondary market senior unsecured debt widening", table_cell_style)
        ],
        [
            Paragraph("Wholesale PD Migration Multiplier", table_cell_style),
            Paragraph(f"{pd_mult:.2f}x", table_cell_bold),
            Paragraph("Default probability acceleration factor", table_cell_style)
        ]
    ]
    t_metrics = Table(metrics_data, colWidths=[160, 90, 280])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('PADDING', (0,0), (-1,-1), 4.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_metrics)
    elements.append(Spacer(1, 8))

    # NLP Drivers
    if key_drivers:
        elements.append(Paragraph("<b>3. Explainable AI (XAI) Lexicon Attribution</b>", bold_style))
        elements.append(Spacer(1, 3))
        driver_str = ", ".join([str(d) for d in key_drivers])
        elements.append(Paragraph(f"<b>Key NLP Driver Tokens:</b> {driver_str}", body_style))
        elements.append(Spacer(1, 8))

    # Committee Direct Actions
    elements.append(Paragraph("<b>4. Recommended Credit Committee Actions</b>", bold_style))
    elements.append(Spacer(1, 3))
    actions = [
        f"&bull; Place {ticker} corporate exposures and counterparties on active Credit Watch with negative outlook." if sentiment_score < 0 else f"&bull; Maintain positive watch on {ticker} commercial lines.",
        "&bull; Execute simulated duration and spread stress test across the wholesale loan book.",
        "&bull; Validate collateral hair-cuts and counterparty credit lines against rating downgrade triggers."
    ]
    for a in actions:
        elements.append(Paragraph(a, body_style))

    doc.build(elements)
    return str(Path(output_path).resolve())


