from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm

NAVY = colors.HexColor("#1F3864"); GREY = colors.HexColor("#555555"); LIGHT = colors.HexColor("#F2F4F8")
H = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=21, textColor=NAVY, leading=25)
SUB = ParagraphStyle("s", fontName="Helvetica", fontSize=11.5, textColor=GREY, leading=15)
SEC = ParagraphStyle("sec", fontName="Helvetica-Bold", fontSize=11.5, textColor=NAVY, spaceBefore=8, spaceAfter=2, leading=14)
B = ParagraphStyle("b", fontName="Helvetica", fontSize=9.4, leading=12.8)
BUL = ParagraphStyle("bul", parent=B, leftIndent=10, bulletIndent=0)
SMALL = ParagraphStyle("sm", parent=B, fontSize=9, textColor=GREY)
PH = ParagraphStyle("ph", parent=B, fontName="Helvetica-Bold", spaceBefore=4)

def sec(t): return [Paragraph(t.upper(), SEC), HRFlowable(width="100%", thickness=0.6, color=NAVY, spaceAfter=4)]
def bullets(items): return [Paragraph(i, BUL, bulletText="•") for i in items]
def project(title, sub, text):
    return KeepTogether([Paragraph(f"{title} <font color='#555555' name='Helvetica'>· {sub}</font>", PH), Paragraph(text, B)])

doc = SimpleDocTemplate("Oseni_Ibrahim_Resume.pdf", pagesize=A4, leftMargin=17*mm, rightMargin=17*mm, topMargin=14*mm, bottomMargin=13*mm,
                        title="Oseni Ibrahim - Resume", author="Oseni Ibrahim")
s = []
s.append(Paragraph("Oseni Ibrahim", H))
s.append(Paragraph("Trading Bot Developer · AI Automation Developer · Full Stack Engineer", SUB))
s.append(Spacer(1, 3))
s.append(Paragraph("Lagos, Nigeria &nbsp;·&nbsp; oseniibrahim845@gmail.com &nbsp;·&nbsp; Fiverr: quamsamuel155 &nbsp;·&nbsp; Upwork", SMALL))
s.append(Spacer(1, 3))

s += sec("Summary")
s.append(Paragraph(
 "Freelance engineer who builds and deploys trading bots, production AI agent systems, automation pipelines and full stack "
 "web apps for clients across the US, UK, Europe and Africa. Sole developer on most engagements, running several in parallel "
 "from scoping to deployment and handover. Strongest in MetaTrader 4/5 automation (MQL4/MQL5 Expert Advisors, trade management "
 "and risk systems), multi agent orchestration (OpenClaw, LangGraph, n8n, Claude API), WhatsApp and CRM automation, and React "
 "dashboards on self managed VPS infrastructure.", B))

s += sec("Skills")
rows = [
 ("Trading automation", "MQL5, MQL4, MetaTrader 4 and 5, Strategy Tester, TradingView and Pine Script, broker and exchange APIs, trade copiers, Telegram signal copiers"),
 ("Trading systems", "Expert Advisors and indicators, MT4 to MT5 conversion, multi-TP trade management, prop-firm risk guards, backtesting, EA monitoring, VPS deployment"),
 ("AI and agents", "Claude API, OpenClaw, LangGraph, Hermes Agent, Gemini, OpenAI, ElevenLabs, HeyGen, ComfyUI"),
 ("Automation", "n8n, Zapier, ManyChat, Evolution API, WhatsApp Cloud API, Twilio, SendGrid"),
 ("Backend", "Python, Node.js, FastAPI, Express"),
 ("Frontend and mobile", "React, TypeScript, Next.js, Flutter, Capacitor"),
 ("Data", "Supabase, PostgreSQL, Pinecone, Qdrant, Google Sheets and Drive"),
 ("Integrations", "GoHighLevel, Shopify, Stripe, Google Calendar, Discord, Slack, Telegram"),
 ("Infrastructure", "Docker, Hetzner, DigitalOcean, Render, Hostinger, Cloudflare Pages"),
]
t = Table([[Paragraph("<b>Area</b>", B), Paragraph("<b>Tools</b>", B)]] + [[Paragraph(a, B), Paragraph(b, B)] for a, b in rows],
          colWidths=[38*mm, 138*mm])
t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("BACKGROUND",(0,0),(-1,0),LIGHT),
    ("LINEBELOW",(0,0),(-1,-1),0.3,colors.HexColor("#D9DDE5")),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
    ("LEFTPADDING",(0,0),(-1,-1),4)]))
s.append(t)

s += sec("Experience")
s.append(Paragraph("<b>Freelance Trading Bot and AI Automation Developer</b> · Fiverr, Upwork, Kwork and direct clients · Remote · Present", B))
s.append(Spacer(1, 2))
s += bullets([
 "Build and maintain trading automation: MT4/MT5 Expert Advisors, TradingView and Pine Script integrations, broker API "
 "integrations, copy-trading systems, crypto trading bots and custom trading dashboards.",
 "Delivered multi agent AI systems with live dashboards for businesses in advertising, luxury transport, trading and real estate.",
 "Built WhatsApp automation for staffing, property management, accounting, lead qualification and merchant onboarding.",
 "Shipped AI video and content pipelines that turn raw footage into edited, captioned and scheduled social posts.",
 "Integrated agents with CRMs and business tools including GoHighLevel, Shopify, Google Workspace, Slack and Discord.",
 "Handle full delivery alone: scoping, milestone pricing, VPS setup, deployment, documentation and client handover.",
 "Also deliver game development work: Roblox systems, Minecraft addons and plugins, and game server setup.",
])

s += sec("Selected Projects")
projects = [
 ("MT4/MT5 Trade Management Toolkit", "MetaTrader, MQL5 and MQL4",
  "Multi-TP signal manager for MT4 and MT5 (one position per take-profit, breakeven after TP1, trailing after TP2, signal "
  "update handling and a restart-safe ticket map), plus a prop-firm style daily loss and drawdown guard that runs beside any EA."),
 ("Multi Agent Trading Operations", "Trading firm, Romania",
  "Expanded an OpenClaw multi agent system with orchestrator routing, Romanian language agents and a PDF to Word pipeline with "
  "OCR fallback. Cut running costs by moving all agents to Claude Haiku."),
 ("Kalshi Trading Bot and Crypto Dashboard", "Private trader",
  "BTC 15 minute prediction market bot as a self hosted web app, plus a real time multi exchange crypto dashboard."),
 ("Ad Operations Mission Control", "Advertising agency",
  "Full stack React dashboard on DigitalOcean running 5 OpenClaw agents on Discord, with agent monitor, memory viewer, chat, "
  "cost tracker and cron pages. Automated ad image generation with Gemini Imagen, a Google Sheets prompt queue, Drive storage "
  "and Discord approval."),
 ("STG Limos AI System", "Luxury transport, Atlanta",
  "8 OpenClaw agents across Discord and Slack with a React and Supabase Mission Control dashboard. Integrated GoHighLevel CRM, "
  "Google Calendar, Obsidian vault sync via GitHub and heartbeat monitoring."),
 ("Rappido WhatsApp Timesheets", "Swiss staffing agencies",
  "Workers submit hours, overtime, surcharges, expenses and absences by WhatsApp to a Node.js bot on Evolution API, backed by "
  "PostgreSQL and an admin dashboard for approvals, weekly reports and CSV export."),
 ("AI Avatar Video and Content Pipeline", "US real estate brokerage",
  "Automated avatar video production with multi milestone GEO rotation, plus a pipeline turning raw phone videos into captioned "
  "posts via Slack, OpusClip and Metricool."),
 ("GetMarketing SaaS", "Marketing platform", "Multi agent marketing dashboard delivered as a full SaaS product."),
 ("Property Management WhatsApp System", "400 rooms across 6 buildings",
  "Rent and tenant management with a WhatsApp Cloud API AI bot, handed over with full client ownership."),
 ("Local AI Business Partner", "Private client",
  "Claude and LangGraph supervisor agent with sub agents running locally on an M4 Mac Mini."),
 ("Industrial Motor Control Retrofit", "Printing press",
  "Python and CSV driven multi motor control system replacing proprietary ink key motors on a Heidelberg press."),
]
for p in projects: s.append(project(*p))

s += sec("Education")
s.append(Paragraph("<b>Computer Science</b> — Federal University of Technology, Akure (FUTA), Nigeria", B))
s += sec("Languages")
s.append(Paragraph("English, German and French (fluent)", B))
doc.build(s)
print("ok")
