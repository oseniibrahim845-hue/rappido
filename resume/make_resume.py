from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm

NAVY = colors.HexColor("#1F3864"); GREY = colors.HexColor("#555555")
H = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=20, textColor=NAVY, leading=24)
SUB = ParagraphStyle("s", fontName="Helvetica", fontSize=11.5, textColor=GREY, leading=15)
SEC = ParagraphStyle("sec", fontName="Helvetica-Bold", fontSize=11.5, textColor=NAVY, spaceBefore=6, spaceAfter=2, leading=14)
B = ParagraphStyle("b", fontName="Helvetica", fontSize=9.2, leading=12.3)
BUL = ParagraphStyle("bul", parent=B, leftIndent=10, bulletIndent=0)
SMALL = ParagraphStyle("sm", parent=B, fontSize=9, textColor=GREY)

def sec(t): return [Paragraph(t.upper(), SEC), HRFlowable(width="100%", thickness=0.6, color=NAVY, spaceAfter=4)]
def bullets(items): return [Paragraph(i, BUL, bulletText="•") for i in items]

doc = SimpleDocTemplate("Oseni_Ibrahim_Resume.pdf", pagesize=A4, leftMargin=17*mm, rightMargin=17*mm, topMargin=12*mm, bottomMargin=11*mm,
                        title="Oseni Ibrahim - Trading Bot Developer (MQL4/MQL5)", author="Oseni Ibrahim")
s = []
s.append(Paragraph("Oseni Ibrahim", H))
s.append(Paragraph("Trading Bot Developer &nbsp;|&nbsp; MQL4 / MQL5 &nbsp;|&nbsp; MetaTrader 4 &amp; 5 Automation", SUB))
s.append(Spacer(1, 3))
s.append(Paragraph('Nigeria (remote) &nbsp;&nbsp;|&nbsp;&nbsp; Email: oseniibrahim845@gmail.com', SMALL))
s.append(Spacer(1, 4))

s += sec("Profile")
s.append(Paragraph("Trading bot developer (MQL5, MQL4, Python, JavaScript/Node.js) specialising in MetaTrader 4 and 5. I build, fix and extend Expert Advisors, indicators "
    "and trade-management tools, with a focus on the details that decide whether an EA behaves correctly on a live account: "
    "broker stop and freeze levels, filling modes, symbol suffixes, restart safety and risk limits. I take on freelance projects and "
    "subcontract work for studios and fintech teams, delivering commented source code to the client's specification.", B))

s += sec("Core Services")
rows = [
 ["EA development", "Custom MT4/MT5 Expert Advisors and indicators built from written rules or specifications"],
 ["Conversion", "MT4 to MT5 ports; TradingView (Pine Script) strategies to MQL5 with signal parity checks"],
 ["Fixes &amp; maintenance", "Debugging, modifying and optimising existing EAs; keeping MT4 and MT5 builds in sync"],
 ["Trade management", "Multi-TP execution, partial closes, breakeven and trailing logic, signal update handling"],
 ["Risk systems", "Prop-firm style daily loss and drawdown guards, exposure limits, news pauses"],
 ["Integrations", "Telegram signal copiers and alerts, trade copiers, TradingView webhooks, broker/exchange APIs, Python bridges"],
 ["Testing &amp; deployment", "Strategy Tester validation, backtesting tools, EA monitoring, VPS deployment"],
]
t = Table([[Paragraph(f"<b>{a}</b>", B), Paragraph(b, B)] for a, b in rows], colWidths=[40*mm, 136*mm])
t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("BOTTOMPADDING",(0,0),(-1,-1),2.5),("TOPPADDING",(0,0),(-1,-1),1),("LEFTPADDING",(0,0),(-1,-1),0)]))
s.append(t)

s += sec("Experience")
s.append(Paragraph("<b>Freelance Software &amp; Automation Developer</b> — self-employed (Fiverr and direct clients) &nbsp;<font color='#555555'>Ongoing</font>", B))
s += bullets([
 "Trading automation: MT4/MT5 Expert Advisors, TradingView/Pine Script integrations, broker API integrations, copy-trading "
 "systems, crypto trading bots and custom trading dashboards.",
 "General development: APIs, AI agents, n8n automation workflows, WhatsApp/chatbot backends and custom web applications.",
])
s.append(Spacer(1, 3))
s.append(Paragraph("<b>AI Automation Developer — Adpeako</b> (remote, client contract) &nbsp;<font color='#555555'>Jun 2026 – Sep 2026</font>", B))
s += bullets([
 "Built an AI automation system on n8n for the Adpeako team, delivered in phases and working inside their Slack, n8n and Google workspace.",
 "Work included AI content tooling and support for product-feed setup in Google Merchant Center; all contracted phases completed, "
 "with a follow-on AI personal-assistant project under discussion.",
])
s.append(Spacer(1, 3))
s.append(Paragraph("<b>Developer — GetMarketing</b> (getmarketing.team) &nbsp;<font color='#555555'>2026</font>", B))
s += bullets([
 "Worked on an AI marketing-strategy web app: Google sign-in, a guided strategy session that generates a custom marketing plan, "
 "and an in-app feedback system that routes user notes to the team by email; fixed user-reported access and feedback issues.",
])

s += sec("Projects")
s.append(Paragraph("<b>Rappido — WhatsApp timesheet &amp; attendance platform</b> (Node.js, Express, PostgreSQL, WhatsApp API) &nbsp;<font color='#555555'>May 2026</font>", B))
s += bullets([
 "Built a WhatsApp chatbot that lets field workers log daily hours, overtime, night/Sunday surcharges, work location and "
 "expenses through a guided menu, plus absence reports and corrections to earlier entries.",
 "Node.js/Express webhook backend with per-user conversation state in PostgreSQL, plus a supervisor dashboard to approve or "
 "reject entries, view weekly reports and charts, and export to CSV.",
])
s.append(Spacer(1, 4))
s.append(Paragraph("<b>MT4/MT5 Trade Management Samples</b> (MQL5, MQL4) &nbsp;<font color='#555555'>2026</font> <br/>github.com/oseniibrahim845-hue/mt4-mt5-trade-management-samples", B))
s += bullets([
 "<b>Multi-TP Signal Manager (MQL5 + MQL4):</b> one position per take-profit level, breakeven after TP1, trailing after TP2, "
 "MOVE_SL / CLOSE channel updates, a ticket map persisted to disk so terminal restarts never duplicate or lose trades, "
 "and stops/freeze-level checks before every modification. The same signal file format drives both platforms.",
 "<b>Daily Loss Guard (MQL5):</b> prop-firm style daily loss and overall drawdown limits measured from the server-day start; "
 "flattens positions, removes pending orders and keeps the account flat for the rest of the day.",
])
s.append(Paragraph("Code walkthroughs or a small paid trial task available on request. Delivered as commented source, tested in the Strategy Tester and on demo.", SMALL))

s += sec("Education")
s.append(Paragraph("<b>Computer Science</b> — Federal University of Technology, Akure (FUTA), Nigeria", B))

doc.build(s)
print("ok")
