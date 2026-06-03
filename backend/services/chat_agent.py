"""LocalFlow AI Chat Agent - conversation engine for tradie websites."""
import re, uuid

AREAS = ["Sydney CBD","Parramatta","Hornsby","Castle Hill","Baulkham Hills","Chatswood","North Sydney","Mosman","Manly","Brookvale","Dee Why","Collaroy","Mona Vale","Newport","Ryde","Gladesville","Epping"]
SERVICES = {"emergency":{"name":"Emergency Repairs","price":"from $550"},"repairs":{"name":"Roof Repairs","price":"from $550"},"restoration":{"name":"Roof Restoration","price":"from $4,500"},"new_roof":{"name":"New Roof Installation","price":"from $8,500"},"gutters":{"name":"Gutter Repairs","price":"from $220"},"inspection":{"name":"Roof Inspections","price":"from $150"}}
PHONE = "1300 273 976"
state = {}

def detect(text):
    t = text.lower()
    if any(w in t for w in ["emergency","urgent","leak","asap"]): return "emergency"
    if any(w in t for w in ["how much","price","cost","quote","$"]): return "pricing"
    for a in AREAS:
        if a.lower() in t: return "area"
    if any(w in t for w in ["area","suburb","near me","sydney"]): return "area"
    if any(w in t for w in ["service","what do you","offer","can you"]): return "services"
    if any(w in t for w in ["about","experience","years","licensed"]): return "about"
    if any(w in t for w in ["phone","call","contact","number"]): return "contact"
    if any(w in t for w in ["hour","open","when","today","saturday"]): return "hours"
    if any(w in t for w in ["book","appoint","schedule","come","visit"]): return "booking"
    if any(w in t for w in ["hi","hello","hey","gday","g'day"]): return "greeting"
    if re.search(r"(my name|name is|i'm|i am|call me)",t): return "lead_info"
    return "general"

def service(text):
    t = text.lower()
    for k,v in SERVICES.items():
        if any(w in t for w in k.split("_") + [v["name"].lower().split()[0]]): return k
    return None

def extract(text):
    info = {}
    m = re.search(r"(?:my name is|i'm|i am|name is|call me|name'?s)\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)",text,re.I)
    if m: info["name"] = m.group(1).strip()
    m = re.search(r"(0[23478]\d{1,2}[\s-]?\d{3}[\s-]?\d{3}|\+61[\s-]?\d+)",text)
    if m: info["phone"] = m.group(1).strip()
    for a in AREAS:
        if a.lower() in text.lower(): info["location"]=a; break
    return info

def process_message(sid, message):
    if not sid or sid == "new":
        sid = uuid.uuid4().hex[:12]
        state[sid] = {"data": {}}
    if sid not in state:
        state[sid] = {"data": {}}
    info = extract(message)
    if info:
        state[sid]["data"].update(info)
    intent = detect(message)
    svc = service(message)
    d = state[sid]["data"]
    has_all = "name" in d and "phone" in d and "location" in d
    def r(text, **kw):
        return {"lead_id":sid,"response":text,"intent":intent,"service":svc,"lead_info":d,"lead_complete":has_all,**kw}
    if has_all:
        return r(f"Thanks **{d['name']}**! Got you in **{d['location']}**. We'll call **{d['phone']}** shortly. Or call us: **{PHONE}**")
    if intent=="lead_info" and "name" in d:
        if "location" not in d: return r("No worries! Which **suburb** are you in?")
        if "phone" not in d: return r(f"Thanks **{d['name']}**! What's the best **phone number** to reach you on?")
    responses = {
        "greeting": "G'day! 👋 Welcome to **Apex Roofing** - Sydney's trusted roofers since 2002. Ask me about pricing, services, or book a free inspection!",
        "emergency": f"🚨 Call us NOW on **{PHONE}** - 24/7 emergency service, 2hr response! Or tell me your name and suburb.",
        "pricing": "Our prices:\n" + "\n".join(f"• **{s['name']}** {s['price']}" for s in SERVICES.values()) + "\n\nFor a free quote tell me your name, suburb and what you need!",
        "area": "We service 18 Sydney suburbs: " + ", ".join(AREAS) + "\nTell me your suburb and I'll confirm!",
        "services": "Full range:\n" + "\n".join(f"• **{s['name']}** {s['price']}" for s in SERVICES.values()) + "\nWhat do you need help with?",
        "about": f"We're Apex Roofing - family-owned since 2002. ⭐4.9★ 200+ reviews. 🛡️Licensed & insured. 7yr warranty.",
        "contact": f"📞 {PHONE}\n📧 info@apexroofing.com.au\nOr tell me your name and number!",
        "hours": "Mon-Fri 7am-5pm, Sat 8am-12pm\n24/7 emergencies - call " + PHONE,
        "booking": "Happy to help! Just tell me:\n1️⃣ Your **name**\n2️⃣ Your **suburb**\n3️⃣ What you **need done**",
        "general": "G'day! 👋 I'm Apex Roofing's AI assistant. Ask about **pricing**, **services**, **service areas**, or **book a visit**!"
    }
    return r(responses.get(intent, responses["general"]))