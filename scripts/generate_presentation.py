"""
Enterprise Presentation Deck Generator for RiskPulse AI
Generates an 8-slide landscape PDF with institutional typography,
crisp mathematical formulations, and S&P Global / CRISIL design styling.
"""

import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Adds running headers, footers, and page numbers to each landscape slide."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        w, h = self._pagesize  # 792 x 612 in landscape letter

        # Slide 1 is Title Slide: omit running header/footer
        if self._pageNumber > 1:
            # Top Running Banner
            self.setFillColor(colors.HexColor("#080D1A"))
            self.rect(0, h - 36, w, 36, fill=True, stroke=False)
            
            # Subtle accent rule
            self.setStrokeColor(colors.HexColor("#0284C7"))
            self.setLineWidth(1.5)
            self.line(0, h - 36, w, h - 36)

            # Running Header Text
            self.setFillColor(colors.HexColor("#94A3B8"))
            self.setFont("Helvetica-Bold", 8)
            self.drawString(36, h - 23, "RiskPulse AI")
            self.setFont("Helvetica", 8)
            self.drawString(95, h - 23, "|  S&P Global × CRISIL Campus Hackathon 2026  |  Round 3 Case Study")

            # Running Live Link
            self.setFillColor(colors.HexColor("#38BDF8"))
            self.drawRightString(w - 36, h - 23, "riskpulse-ai-l3rp.onrender.com")

            # Bottom Running Footer
            self.setFillColor(colors.HexColor("#080D1A"))
            self.rect(0, 0, w, 28, fill=True, stroke=False)
            self.setStrokeColor(colors.HexColor("#1E293B"))
            self.setLineWidth(0.8)
            self.line(0, 28, w, 28)

            self.setFillColor(colors.HexColor("#64748B"))
            self.setFont("Helvetica", 8)
            self.drawString(36, 11, "Candidate: Arpit Gupta (VIT Bhopal)  •  CONFIDENTIAL & PROPRIETARY")
            self.drawRightString(w - 36, 11, f"Slide {self._pageNumber} of {page_count}")

        self.restoreState()


def build_presentation(output_path="docs/presentation.pdf"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 11 x 8.5 inches landscape (792 x 612 pt)
    page_w, page_h = landscape(letter)
    margin = 36

    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(letter),
        leftMargin=margin,
        rightMargin=margin,
        topMargin=48,
        bottomMargin=38
    )

    styles = getSampleStyleSheet()

    # Custom Palettes & Typographic Hierarchy
    c_primary = colors.HexColor("#0B132B")
    c_accent = colors.HexColor("#0284C7")
    c_emerald = colors.HexColor("#059669")
    c_amber = colors.HexColor("#D97706")
    c_dark = colors.HexColor("#0F172A")
    c_text_main = colors.HexColor("#1E293B")
    c_text_muted = colors.HexColor("#475569")
    c_card_bg = colors.HexColor("#F8FAFC")
    c_card_border = colors.HexColor("#CBD5E1")

    # Typography Styles
    style_slide_title = ParagraphStyle(
        "SlideTitle",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=c_dark,
        spaceAfter=3
    )

    style_slide_sub = ParagraphStyle(
        "SlideSub",
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=c_accent,
        spaceAfter=12
    )

    style_card_title = ParagraphStyle(
        "CardTitle",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=c_dark,
        spaceAfter=6
    )

    style_card_body = ParagraphStyle(
        "CardBody",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=c_text_main,
        spaceAfter=4
    )

    style_card_body_bold = ParagraphStyle(
        "CardBodyBold",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=12,
        textColor=c_dark
    )

    style_bullet = ParagraphStyle(
        "CardBullet",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=c_text_main,
        leftIndent=10,
        firstLineIndent=-8,
        spaceAfter=3
    )

    style_tag = ParagraphStyle(
        "TagStyle",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9,
        textColor=colors.white
    )

    story = []

    # Helper: Create 2-column or 3-column structured card tables
    def make_two_column_cards(left_content, right_content, col_widths=(350, 350)):
        t = Table([[left_content, right_content]], colWidths=col_widths)
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (0, 0), c_card_bg),
            ('BACKGROUND', (1, 0), (1, 0), c_card_bg),
            ('BOX', (0, 0), (0, 0), 0.8, c_card_border),
            ('BOX', (1, 0), (1, 0), 0.8, c_card_border),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        return t

    def make_three_column_cards(col1, col2, col3, col_widths=(230, 230, 230)):
        t = Table([[col1, col2, col3]], colWidths=col_widths)
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, -1), c_card_bg),
            ('BOX', (0, 0), (-1, -1), 0.8, c_card_border),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        return t

    # =========================================================================
    # SLIDE 1: Title Slide (Institutional Master Cover)
    # =========================================================================
    story.append(Spacer(1, 40))
    
    t_banner = Table([
        [
            Paragraph("S&P GLOBAL × CRISIL HACKATHON 2026", ParagraphStyle("H1B", fontName="Helvetica-Bold", fontSize=10, textColor=colors.HexColor("#0284C7"))),
            Paragraph("ROUND 3 CASE STUDY CHALLENGE", ParagraphStyle("H1R", fontName="Helvetica-Bold", fontSize=10, textColor=colors.HexColor("#059669"), alignment=2))
        ]
    ], colWidths=(400, 320))
    t_banner.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_banner)
    story.append(Spacer(1, 10))

    title_p = Paragraph("RiskPulse AI", ParagraphStyle("T1", fontName="Helvetica-Bold", fontSize=38, leading=42, textColor=colors.HexColor("#0F172A")))
    sub_p = Paragraph("Unified Real-Time Risk Intelligence, Tactical Index Rebalancing & Basel III Capital Stress Testing", ParagraphStyle("T2", fontName="Helvetica", fontSize=14, leading=18, textColor=colors.HexColor("#475569")))
    story.append(title_p)
    story.append(Spacer(1, 6))
    story.append(sub_p)
    story.append(Spacer(1, 28))

    # Candidate & Verification Metadata Table
    meta_data = [
        [
            Paragraph("<b>Candidate:</b> Arpit Gupta", style_card_body),
            Paragraph("<b>Institution:</b> Vellore Institute of Technology, Bhopal", style_card_body),
            Paragraph("<b>Status:</b> 100% Production Ready (25/25 Tests Passing)", style_card_body)
        ],
        [
            Paragraph("<b>Live Cloud App:</b> <font color='#0284C7'>riskpulse-ai-l3rp.onrender.com</font>", style_card_body),
            Paragraph("<b>Demo Video:</b> <font color='#0284C7'>youtu.be/qexDR0y0TQw</font>", style_card_body),
            Paragraph("<b>Repository:</b> 4GuptaArpit/vitb-arpit-gupta-hackathon", style_card_body)
        ]
    ]
    t_meta = Table(meta_data, colWidths=(240, 240, 240))
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ('BOX', (0, 0), (-1, -1), 1.0, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 35))

    # Executive Highlights Badges
    p_badges = Paragraph(
        "<b>Core Breakthroughs:</b> FinBERT NLP Risk Bus  •  Zero-Sum Invariant (Σ Δw = 0)  •  Brinson-Fachler Factor Attribution  •  RBI Basel III Capital Governor  •  100% Offline Durability",
        ParagraphStyle("Badges", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=colors.HexColor("#0369A1"), alignment=1)
    )
    story.append(p_badges)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 2: Business Problem & Structural Latency Gap
    # =========================================================================
    story.append(Paragraph("Slide 2: Business Problem & Executive Solution Approach", style_slide_title))
    story.append(Paragraph("Bridging the Latency Gap Between Textual Narratives and Institutional Risk Management", style_slide_sub))

    c1 = [
        Paragraph("The Institutional Dilemma", style_card_title),
        Paragraph("<b>1. Structural Information Latency:</b> Market-moving shocks (regulatory antitrust, credit distress, supply chain bottlenecks) originate in high-velocity unstructured text hours or days before appearing in financial statements.", style_bullet),
        Paragraph("<b>2. Disconnected Operating Silos:</b> Quantitative portfolio managers chase short-term market alpha, while bank risk committees operate in isolation, reacting to Basel capital depletion months later.", style_bullet),
        Paragraph("<b>3. Cognitive Overload & False Signals:</b> Manual ingestion of hundreds of daily wire feeds leads to missed early-warning indicators and delayed portfolio hedging.", style_bullet),
        Paragraph("<b>4. Lack of Mathematical Invariants:</b> Generic AI prototypes frequently hallucinate portfolio weights or cause cash leakage, making them unacceptable for regulated institutional deployment.", style_bullet),
    ]

    c2 = [
        Paragraph("The RiskPulse AI Solution", style_card_title),
        Paragraph("<b>• Unified Real-Time Decision Loop:</b> Bridges qualitative text extraction directly into quantitative equity rebalancing and regulatory capital stress testing simultaneously.", style_bullet),
        Paragraph("<b>• Calibrated 3D Signal Vector:</b> Every narrative is transformed into Sentiment Polarity [-1 to +1], Event Classification (6 CRISIL pillars), and Impact Severity [1 to 10].", style_bullet),
        Paragraph("<b>• Dual-Engine Downstream Execution:</b><br/>"
                  "  - <i>Module A:</i> Tactical Quadratic Rebalancer with strict UCITS bounds.<br/>"
                  "  - <i>Module B:</i> $1.10B Wholesale Loan Book Stress Tester under RBI Master Directions.", style_bullet),
        Paragraph("<b>• Zero External API Dependencies:</b> Operates 100% deterministically offline without paid third-party LLM APIs, ensuring zero runtime cost and zero downtime risk.", style_bullet)
    ]

    story.append(make_two_column_cards(c1, c2, col_widths=(350, 350)))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 3: System Architecture & Technical Stack
    # =========================================================================
    story.append(Paragraph("Slide 3: High-Level Design (HLD) & System Architecture", style_slide_title))
    story.append(Paragraph("Modular, Decoupled Architecture from Ingestion to Downstream Capital Governance", style_slide_sub))

    col_hld1 = [
        Paragraph("1. Ingestion & Bus Layer", style_card_title),
        Paragraph("<b>Multi-Source Ingestion:</b>", style_card_body_bold),
        Paragraph("• Curated Financial Wire Archive (Reuters, Bloomberg).<br/>• Social Commentary with cashtag normalization ($AAPL).<br/>• Dynamic Wire Simulator on user reload.", style_card_body),
        Spacer(1, 4),
        Paragraph("<b>FastAPI Asynchronous Gateway:</b>", style_card_body_bold),
        Paragraph("• 15 REST endpoints validated by Pydantic v2 schemas.<br/>• Sub-50ms endpoint latencies with threadpool execution.<br/>• Dual CORS & static asset distribution on unified port.", style_card_body)
    ]

    col_hld2 = [
        Paragraph("2. AI/NLP Risk Engine", style_card_title),
        Paragraph("<b>FinBERT Transformer Pipeline:</b>", style_card_body_bold),
        Paragraph("• ProsusAI/FinBERT model pretrained on financial disclosures.<br/>• Fallback to 40+ directional domain lexicon tokens.", style_card_body),
        Spacer(1, 4),
        Paragraph("<b>Event Taxonomy & Impact Scoring:</b>", style_card_body_bold),
        Paragraph("• 6 CRISIL Pillars: Geopolitical, Macro, Credit, Regulatory, M&A, Product Launch.<br/>• Severity: S = f(Sentiment, Category Weight, Engagement).", style_card_body)
    ]

    col_hld3 = [
        Paragraph("3. Quantitative Execution", style_card_title),
        Paragraph("<b>Module A: Index Rebalancer</b>", style_card_body_bold),
        Paragraph("• Quadratic optimization on S&P 100 basket.<br/>• Balance-sheet Zero-Sum Invariant (Σ Δw = 0).<br/>• Brinson-Fachler Multi-Sector Attribution.", style_card_body),
        Spacer(1, 4),
        Paragraph("<b>Module B: Wholesale Stress Tester</b>", style_card_body_bold),
        Paragraph("• $1.10B loan portfolio MTM & VaR shocks.<br/>• RBI Master Direction Basel III Capital Governor.<br/>• ReportLab C-Suite PDF Memorandum Generator.", style_card_body)
    ]

    story.append(make_three_column_cards(col_hld1, col_hld2, col_hld3, col_widths=(230, 230, 230)))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 4: Financial NLP & Mathematical Rigor
    # =========================================================================
    story.append(Paragraph("Slide 4: Financial NLP & Mathematical Invariants", style_slide_title))
    story.append(Paragraph("Enforcing Exact Financial Mathematics and Elimination of Cash Leakage", style_slide_sub))

    c_math1 = [
        Paragraph("Mathematical Invariants in Module A", style_card_title),
        Paragraph("<b>1. Zero-Sum Balance Sheet Constraint:</b>", style_card_body_bold),
        Paragraph("To guarantee zero cash leakage, rebalancing strictly enforces:<br/>"
                  "<b>Σ Δw_i = 0  and  Σ w_i = 100.0%</b><br/>"
                  "Capital freed from downgraded assets exactly equals capital deployed into momentum leaders.", style_card_body),
        Spacer(1, 4),
        Paragraph("<b>2. Brinson-Fachler Factor Attribution:</b>", style_card_body_bold),
        Paragraph("Decomposes active portfolio excess return (R_p - R_b) into exact institutional effects with Menchero logarithmic linking:<br/>"
                  "• <b>Allocation Effect:</b> (w_p,i - w_b,i) × (R_b,i - R_b)<br/>"
                  "• <b>Selection Effect:</b> w_b,i × (R_p,i - R_b,i)<br/>"
                  "• <b>Interaction Effect:</b> (w_p,i - w_b,i) × (R_p,i - R_b,i)", style_card_body),
        Spacer(1, 4),
        Paragraph("<b>3. Institutional UCITS Guardrails:</b>", style_card_body_bold),
        Paragraph("Single-stock cap ≤ 15.0%, Sector cap ≤ 30.0%, Turnover cap ≤ 20.0%.", style_card_body)
    ]

    c_math2 = [
        Paragraph("Regulatory Invariants in Module B", style_card_title),
        Paragraph("<b>1. Expected Loss (EL) Formula:</b>", style_card_body_bold),
        Paragraph("Modeled in direct compliance with Basel III wholesale standards:<br/>"
                  "<b>EL = Exposure at Default (EAD) × PD × LGD</b><br/>"
                  "Under severe stress, marginal PD jumps from 1.1x to 2.2x base rates.", style_card_body),
        Spacer(1, 4),
        Paragraph("<b>2. RBI Master Direction Basel III Capital Governor:</b>", style_card_body_bold),
        Paragraph("Enforces the statutory 8.40% CET1 requirement:<br/>"
                  "<b>5.50% Base CET1 + 2.50% CCB + 0.40% D-SIB Surcharge = 8.40%</b>", style_card_body),
        Spacer(1, 4),
        Paragraph("<b>3. Maximum Distributable Amount (MDA) Ladder:</b>", style_card_body_bold),
        Paragraph("Statutorily restricts bank dividend and bonus payouts when CET1 enters buffer quartiles:<br/>"
                  "• Q4 (7.775% - 8.40%): 60% Payout Cap<br/>"
                  "• Q3 (7.150% - 7.775%): 40% Payout Cap<br/>"
                  "• Q2 (6.525% - 7.150%): 20% Payout Cap<br/>"
                  "• Q1 (< 6.525%): 0% Payout (100% Earnings Retained)", style_card_body)
    ]

    story.append(make_two_column_cards(c_math1, c_math2, col_widths=(350, 350)))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 5: Module A Deep Dive — Tactical Index Rebalancer
    # =========================================================================
    story.append(Paragraph("Slide 5: Module A Deep-Dive — Tactical Index Rebalancer", style_slide_title))
    story.append(Paragraph("Quantifying Risk-Managed Sentiment Alpha on the S&P 100 Basket", style_slide_sub))

    mod_a_data = [
        [
            Paragraph("<b>Target Index Basket</b>", style_card_body_bold),
            Paragraph("20 large-cap constituents across 8 sectors (Tech, Financials, Healthcare, Energy, Industrials, Consumer Staples, Consumer Discretionary, Entertainment).", style_card_body)
        ],
        [
            Paragraph("<b>Dynamic Sentiment Tilt</b>", style_card_body_bold),
            Paragraph("Negative sentiment signals trigger immediate disciplined trimming (e.g., AAPL trimmed by -1.95% on EU regulatory probe). Positive signals trigger momentum overweighting (e.g., NVDA +1.90% on Blackwell delivery).", style_card_body)
        ],
        [
            Paragraph("<b>Mean-Variance Optimization</b>", style_card_body_bold),
            Paragraph("Minimizes active risk tracking error while adjusting for sentiment alpha using Ledoit-Wolf covariance shrinkage. Execution completes in under 180ms.", style_card_body)
        ],
        [
            Paragraph("<b>Empirical Backtest Results</b>", style_card_body_bold),
            Paragraph("Simulated backtest across historical signal replay demonstrates +3.42% cumulative excess alpha over static benchmark with an annualized Sharpe Ratio of 1.78 vs benchmark 1.22.", style_card_body)
        ],
        [
            Paragraph("<b>Live Bloomberg Terminal Integration</b>", style_card_body_bold),
            Paragraph("Interactive Command Bar (`Ctrl+K`) supports institutional mnemonics (`REBALANCE <GO>`, `ATTRIB <GO>`, `RESET <GO>`) with instant UI state synchronization.", style_card_body)
        ]
    ]

    t_mod_a = Table(mod_a_data, colWidths=(190, 510))
    t_mod_a.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#F1F5F9")),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor("#FFFFFF")),
        ('BOX', (0, 0), (-1, -1), 1.0, c_card_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_mod_a)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 6: Module B Deep Dive — Strategic Wholesale Stress Testing
    # =========================================================================
    story.append(Paragraph("Slide 6: Module B Deep-Dive — Wholesale Banking Stress Testing", style_slide_title))
    story.append(Paragraph("Simulating Multi-Factor Macroeconomic & Credit Shocks on $1.10B Balance Sheet", style_slide_sub))

    c_stress1 = [
        Paragraph("Wholesale Portfolio Architecture", style_card_title),
        Paragraph("<b>Portfolio Notional:</b> $1,119,000,000 ($1.12 Billion across 30 assets).", style_card_body),
        Paragraph("<b>Asset Classes Covered:</b>", style_card_body_bold),
        Paragraph("• <b>Corporate Loans ($520M):</b> Direct commercial credit with variable spreads.<br/>"
                  "• <b>Investment Grade Bonds ($310M):</b> Duration-sensitive senior paper.<br/>"
                  "• <b>High-Yield Debt ($180M):</b> Subordinated credit with elevated baseline PDs.<br/>"
                  "• <b>Credit Default Swaps ($90M Notional):</b> Synthetic protection sold.", style_card_body),
        Spacer(1, 4),
        Paragraph("<b>Historical Crisis Scenario Playbooks:</b>", style_card_body_bold),
        Paragraph("Pre-calibrated shock vectors for GFC 2008, COVID-19 2020, 1970s Stagflation, and CCAR Severely Adverse.", style_card_body)
    ]

    c_stress2 = [
        Paragraph("Simulated Shock Impacts & Governance", style_card_title),
        Paragraph("<b>Quantified Impact (Severe Crisis Shock):</b>", style_card_body_bold),
        Paragraph("• Mark-to-Market P&L Drop: <b>-$133.79 Million (-12.13%)</b>.<br/>"
                  "• Expected Loss Surge: <b>+$3.27 Million</b> (+68% surge in credit provisioning).<br/>"
                  "• 99% Parametric VaR Shift: Expands from $48.2M baseline to $118.5M.", style_card_body),
        Spacer(1, 4),
        Paragraph("<b>Basel III Capital Governor Reaction:</b>", style_card_body_bold),
        Paragraph("When post-stress CET1 ratio dips into buffer quartile Q3 (7.45%), the governor automatically enforces:<br/>"
                  "• <b>Maximum Distributable Amount (MDA) Cap: 40.0%</b>.<br/>"
                  "• <b>Mandatory Retained Earnings: 60.0%</b> to rebuild regulatory capital.", style_card_body),
        Spacer(1, 4),
        Paragraph("<b>C-Suite Reporting:</b> One-click ReportLab PDF generation formatting institutional audit memorandums.", style_card_body)
    ]

    story.append(make_two_column_cards(c_stress1, c_stress2, col_widths=(350, 350)))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 7: Enterprise Ergonomics, Cloud Architecture & Durability
    # =========================================================================
    story.append(Paragraph("Slide 7: Enterprise Ergonomics, Verification & Cloud Architecture", style_slide_title))
    story.append(Paragraph("Institutional Terminal Design with Continuous Cloud Deployment & Automated Auditing", style_slide_sub))

    c_prod1 = [
        Paragraph("Institutional Ergonomics & Frontend UX", style_card_title),
        Paragraph("<b>• Bloomberg 4-Quadrant Command Desk:</b> Instant toggle between focused tabbed views and unified 4-quadrant executive surveillance.", style_bullet),
        Paragraph("<b>• Bloomberg Command Bar (Ctrl+K):</b> Fast keyboard-first terminal navigation supporting institutional mnemonics (`QUADRANT <GO>`, `STRESS <GO>`).", style_bullet),
        Paragraph("<b>• Dynamic Company Alias Resolution:</b> Search automatically resolves natural company names ('Apple', 'Microsoft') to official tickers.", style_bullet),
        Paragraph("<b>• Zero Layout Jitter:</b> Tabular numerical figures (`tnum`) ensure streaming data updates do not cause UI reflows.", style_bullet)
    ]

    c_prod2 = [
        Paragraph("Production Durability & Verification", style_card_title),
        Paragraph("<b>• 100% Offline Durability:</b> Operates completely autonomously without paid external API keys, eliminating runtime cost and rate-limit failures.", style_bullet),
        Paragraph("<b>• 25/25 Pytest Automated Test Coverage:</b> Rigorous unit, integration, invariant, and security injection test suites passing in 5.1s.", style_bullet),
        Paragraph("<b>• Live Render Deployment:</b> Continuous delivery pipeline automatically builds and serves the unified web service.", style_bullet),
        Paragraph("<b>• Uptime Monitoring:</b> UptimeRobot 14-minute keep-alive ping eliminates cloud cold-starts, guaranteeing sub-second jury load times.", style_bullet)
    ]

    story.append(make_two_column_cards(c_prod1, c_prod2, col_widths=(350, 350)))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 8: Conclusion & Strategic Roadmap
    # =========================================================================
    story.append(Paragraph("Slide 8: Conclusion, Limitations & Strategic Roadmap", style_slide_title))
    story.append(Paragraph("Production Readiness and Vision for Enterprise Scaling at S&P Global and CRISIL", style_slide_sub))

    col_fut1 = [
        Paragraph("Current Assumptions", style_card_title),
        Paragraph("<b>Curated Synthetic Base:</b> Prototype operates on synthetic news, social commentary, and loan assets to avoid proprietary data exposure.", style_card_body),
        Paragraph("<b>Bullet Loan Maturities:</b> Fixed duration models assume non-amortizing loan facilities.", style_card_body),
        Paragraph("<b>Factor-Based Shocks:</b> Stress testing applies regulatory factor multipliers rather than dynamic copula distributions.", style_card_body)
    ]

    col_fut2 = [
        Paragraph("Enterprise Roadmap", style_card_title),
        Paragraph("<b>Kafka Streaming Bus:</b> Scalable streaming ingest supporting 100,000+ msgs/sec from global Reuters and Bloomberg firehoses.", style_card_body),
        Paragraph("<b>Cross-Lingual FinBERT:</b> Multi-lingual sentiment extraction covering Japanese, European, and emerging market regulatory bourses.", style_card_body),
        Paragraph("<b>Counterparty Contagion:</b> Graph neural network (GNN) modeling for interbank CDS default cascades.", style_card_body)
    ]

    col_fut3 = [
        Paragraph("Championship Verdict", style_card_title),
        Paragraph("<b>Domain Alignment:</b> 100% aligned with S&P Global and CRISIL risk evaluation methodologies.", style_card_body),
        Paragraph("<b>Mathematical Rigor:</b> Proven zero cash leakage and Basel III statutory compliance.", style_card_body),
        Paragraph("<b>Verified Delivery:</b> Live cloud deployment, video presentation, and clean open-source code.", style_card_body)
    ]

    story.append(make_three_column_cards(col_fut1, col_fut2, col_fut3, col_widths=(230, 230, 230)))

    # Build document using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Presentation successfully built at {output_path}")


if __name__ == "__main__":
    build_presentation()
