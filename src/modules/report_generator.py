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
    """Compiles an institutional CRISIL-grade PDF risk memorandum."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
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
        fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=NAVY, spaceAfter=4
    )
    sub_style = ParagraphStyle(
        'RepSub', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=SKY, spaceAfter=14
    )
    body_style = ParagraphStyle(
        'RepBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=14, textColor=colors.HexColor("#334155")
    )
    bold_style = ParagraphStyle(
        'RepBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9.5, leading=14, textColor=NAVY
    )

    elements = []

    # Title & Header
    elements.append(Paragraph("RISKPULSE AI — EXECUTIVE STRESS TEST MEMORANDUM", title_style))
    elements.append(Paragraph(f"S&P GLOBAL × CRISIL HACKATHON 2026 | SCENARIO: {result.event_type.upper()} (SEVERITY: {result.impact_score}/10)", sub_style))
    elements.append(Spacer(1, 8))

    # Executive Summary Box
    summary_text = (
        f"This memorandum presents the simulated impact of a high-severity {result.event_type} event "
        f"(calibrated severity score of {result.impact_score}/10) on the institutional wholesale banking portfolio ($1.10B baseline notional). "
        f"Multi-factor shocks were applied across credit spread widening, rating migration PD multipliers, and duration-adjusted mark-to-market prices."
    )
    elements.append(Paragraph(summary_text, body_style))
    elements.append(Spacer(1, 14))

    # Key Metrics Table
    elements.append(Paragraph("<b>1. Summary Impact Metrics</b>", bold_style))
    elements.append(Spacer(1, 4))

    metrics_data = [
        ["Metric", "Pre-Stress Baseline", "Post-Stress Stressed", "Net Variance / Impact"],
        ["Portfolio Market Value", f"${result.baseline_value_usd/1e6:,.2f}M", f"${result.stressed_value_usd/1e6:,.2f}M", f"${result.total_pnl_usd/1e6:,.2f}M ({result.pnl_percentage:.2f}%)"],
        ["Expected Loss (EL = EAD*PD*LGD)", f"${result.baseline_expected_loss_usd/1e6:,.2f}M", f"${result.stressed_expected_loss_usd/1e6:,.2f}M", f"+${result.el_increase_usd/1e6:,.2f}M"],
        ["99% Value-at-Risk (VaR)", f"${result.var_99_baseline_usd/1e6:,.2f}M", f"${result.var_99_stressed_usd/1e6:,.2f}M", f"+${(result.var_99_stressed_usd - result.var_99_baseline_usd)/1e6:,.2f}M"]
    ]
    t_metrics = Table(metrics_data, colWidths=[160, 120, 120, 130])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TEXTCOLOR', (3,1), (3,-1), ROSE),
        ('FONTNAME', (3,1), (3,-1), 'Helvetica-Bold'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_metrics)
    elements.append(Spacer(1, 16))

    # Asset Class Breakdown Table
    elements.append(Paragraph("<b>2. Asset Class Drawdown Breakdown</b>", bold_style))
    elements.append(Spacer(1, 4))

    asset_headers = ["Asset Class", "Positions", "Baseline ($M)", "Stressed ($M)", "Drawdown ($M)", "Loss (%)"]
    asset_rows = [asset_headers]
    for b in result.asset_breakdown:
        asset_rows.append([
            b["asset_type"],
            str(b["positions_count"]),
            f"${b['baseline_mv_usd']/1e6:,.2f}M",
            f"${b['stressed_mv_usd']/1e6:,.2f}M",
            f"${b['pnl_usd']/1e6:,.2f}M",
            f"{b['pnl_pct']:.2f}%"
        ])
    t_assets = Table(asset_rows, colWidths=[150, 60, 80, 80, 85, 75])
    t_assets.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SLATE),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_assets)
    elements.append(Spacer(1, 20))

    # Committee Recommendation Footer
    elements.append(Paragraph("<b>3. Risk Committee Next Actions</b>", bold_style))
    elements.append(Spacer(1, 4))
    recs = [
        "1. Active hedging via interest rate swaps to offset duration MTM drag.",
        "2. Review collateral hair-cuts and credit limits on high-yield debt counterparties.",
        "3. Reallocate derivative protections to curtail CDS mark-to-market exposure."
    ]
    for r in recs:
        elements.append(Paragraph(r, body_style))

    doc.build(elements)
    return str(Path(output_path).resolve())
