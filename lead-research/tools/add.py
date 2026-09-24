# usage: python3 add.py outfile <<'X' ... X   (one row per line, fields separated by ' ;; ')
# company ;; website ;; country ;; city ;; type ;; industry ;; product ;; acct ;; erp ;; pay ;; email ;; email_src ;; intent ;; detail ;; workflow ;; source ;; evidence ;; evtype ;; notes ;; [contact full ;; title]
import sys, json, hashlib
TYPEMAP={"inv":"Invoicing Software","acc":"Accounting Software","ar":"Accounts Receivable Software","ei":"E-Invoicing","bill":"Billing & Subscription Management","firm":"Accounting & Bookkeeping Firm","erp":"ERP Implementation & Consulting","pay":"Payments & Fintech","bms":"Business Management Software","fas":"Financial Administration Services"}
SUBJ=["{w} at {c}","Automating {w} for {c}","A possible automation for {c}'s finance workflow","{c}: an AI agent for {w}","Idea for {c}'s invoice operations","OpenClaw agent for {c}"]
REASON={"Invoicing Software":"An invoicing product generates constant invoice status, reminder and reporting work that an agent can take on for the team or its customers.",
"Accounting Software":"An accounting platform sits at the centre of invoice, reconciliation and reporting data, which suits agent-driven finance admin.",
"Accounts Receivable Software":"AR platforms revolve around invoice follow ups, payment matching and collections reporting, which are natural agent workflows.",
"E-Invoicing":"E-invoicing providers handle high volumes of structured invoice documents, status events and exceptions that need monitoring.",
"Billing & Subscription Management":"Recurring billing creates repeated invoice, dunning and revenue reporting tasks that are well suited to automation.",
"Accounting & Bookkeeping Firm":"Bookkeeping firms repeat invoice processing, chasing and reporting across many client ledgers every month.",
"ERP Implementation & Consulting":"ERP consultants design finance workflows for clients and can add agent-based invoice and reporting automation to projects.",
"Payments & Fintech":"Payment platforms sit next to invoice and reconciliation data, where status monitoring and reporting can be automated.",
"Business Management Software":"Business management suites combine billing, CRM and accounting data, which creates cross-system invoice admin work.",
"Financial Administration Services":"Outsourced finance providers run invoice, collections and reporting processes for many clients at once."}
out=sys.argv[1]; n=0
with open(out,"a") as fh:
  for line in sys.stdin:
    line=line.strip()
    if not line or line.startswith("#"): continue
    f=[x.strip() for x in line.split(";;")]
    f+=[""]*(21-len(f))
    c,web,country,city,t,ind,prod,acct,erp,pay,email,esrc,intent,detail,wf,src,ev,evt,notes,person,title=f[:21]
    t=TYPEMAP.get(t,t)
    h=int(hashlib.md5(c.encode()).hexdigest(),16)
    short=wf.split(" and ")[0]
    subj=SUBJ[h%len(SUBJ)].format(c=c,w=short[:1].upper()+short[1:] if SUBJ[h%len(SUBJ)].startswith("{w}") else short)
    d=detail[0].lower()+detail[1:] if detail.startswith("The ") else detail
    opening=("I noticed that " if h%2 else "I saw that ")+ d.replace("The company", c).replace("the company", c)
    fn=person.split()[0] if person else ""
    row=dict(company=c,website=web,country=country,state="",city=city,company_type=t,industry=ind,invoice_product_or_service=prod,accounting_platform=acct,erp=erp,payment_platform=pay,company_size="",linkedin="",contact_full_name=person,first_name=fn,job_title=title,email=email,email_source=esrc,buying_intent=intent,automation_opportunity="Potential opportunity: automate "+wf+".",personalization_detail=detail,personalization_reason=REASON.get(t,""),personalized_opening=opening,subject_line=subj,workflow_phrase=wf,source_url=src,evidence=ev,evidence_type=evt,research_confidence="High" if email else "Medium",notes=notes)
    fh.write(json.dumps(row,ensure_ascii=False)+"\n"); n+=1
print("wrote",n)
