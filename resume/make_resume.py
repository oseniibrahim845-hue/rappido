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
s.append(Paragraph('Nigeria (remote) &nbsp;&nbsp;|&nbsp;&nbsp; Email: oseniibrahim845@gmail.com &nbsp;&nbsp;|&nbsp;&nbsp; GitHub: github.com/oseniibrahim845-hue', SMALL))
s.append(Spacer(1, 4))

s += sec("Profile")
s.append(Paragraph("Trading bot developer specialising in MetaTrader 4 and 5. I build, fix and extend Expert Advisors, indicators "
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
 ["Integrations", "Telegram signal copiers and alerts, TradingView webhooks, broker/exchange APIs, Python bridges"],
 ["Trade copiers", "Account-to-account copiers with symbol mapping and lot scaling"],
 ["Testing &amp; deployment", "Strategy Tester validation, backtesting tools, EA monitoring, VPS deployment"],
]
t = Table([[Paragraph(f"<b>{a}</b>", B), Paragraph(b, B)] for a, b in rows], colWidths=[40*mm, 136*mm])
t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("BOTTOMPADDING",(0,0),(-1,-1),2.5),("TOPPADDING",(0,0),(-1,-1),1),("LEFTPADDING",(0,0),(-1,-1),0)]))
s.append(t)

s += sec("Technical Skills")
s += bullets([
 "<b>Languages:</b> MQL5, MQL4, Python, JavaScript/TypeScript (Node.js)",
 "<b>Platforms:</b> MetaTrader 4, MetaTrader 5 (terminal and Strategy Tester), TradingView",
 "<b>Integration:</b> WebRequest/REST, sockets and file-based bridges, Telegram Bot API, webhook receivers",
 "<b>Practices:</b> restart-safe state handling, broker-rule validation before every order change, commented and reviewable code",
])

s += sec("Projects")
s.append(Paragraph("<b>Rappido — WhatsApp timesheet &amp; attendance platform</b> (Node.js, Express, PostgreSQL, WhatsApp API) &nbsp;<font color='#555555'>2026</font>", B))
s += bullets([
 "Built a WhatsApp chatbot that lets field workers log daily hours, overtime, night/Sunday surcharges, work location and "
 "expenses through a guided menu, plus absence reports and corrections to earlier entries.",
 "Webhook backend in Node.js/Express with per-user conversation state stored in PostgreSQL, input validation at every step "
 "and weekly summaries sent back to each worker.",
 "Web dashboard for supervisors to filter, approve or reject entries, view weekly reports and charts, and export data to CSV.",
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
s.append(Paragraph("Code walkthroughs or a small paid trial task are available on request.", SMALL))

s += sec("Education")
s.append(Paragraph("<b>Computer Science</b> — Federal University of Technology, Nigeria", B))

s += sec("How I Work")
s += bullets([
 "Clear written scope and a fixed quote per project before work starts",
 "Delivery as commented source code, tested in the Strategy Tester and on a demo account",
 "Available for white-label and NDA subcontracting",
])
doc.build(s)
print("ok")
