#!/usr/bin/env python3
"""LocalFlow Site Generator - generates a tradie website + includes AI widget."""
import argparse, os, subprocess
from datetime import datetime

SERVICE_CARD = '<div class="card"><h3>NAME</h3><p>Professional NAME service by BIZ.</p>PRICE</div>'
AREA_BADGE = '<span>AREA</span>'
TESTIMONIAL = '<div class="testimonial"><div class="stars">STARS</div><p>"TEXT"</p><div class="author">NAME<br><span>LOC</span></div></div>'

def gen(name, biz_type, phone, email, areas_str, services_str, output_dir, serve):
    areas = [a.strip() for a in areas_str.split(",")]
    services = []
    for s in services_str.split(","):
        parts = s.split(":")
        services.append({"name": parts[0].strip(), "price": "from $" + parts[1].strip() if len(parts) > 1 else ""})
    
    emojis = {"roofing":"🔨","plumbing":"🔧","electrical":"⚡","hvac":"❄️","landscaping":"🌱","painting":"🎨"}
    emoji = emojis.get(biz_type, "🔨")
    phone_raw = phone.replace(" ", "")
    bid = name.lower().replace("'","").replace(" ","-")[:20]
    area_short = ", ".join(areas[:3])
    
    # Build service cards
    sc = ""
    for s in services:
        card = SERVICE_CARD.replace("NAME", s["name"]).replace("BIZ", name)
        if s["price"]:
            card = card.replace("PRICE", '<div class="price">'+s["price"]+'</div>')
        else:
            card = card.replace("PRICE", "")
        sc += card
    
    # Build area badges
    ab = ""
    for a in areas:
        ab += AREA_BADGE.replace("AREA", a)
    
    # Build testimonials
    tc = ""
    tests = [
        ("Amazing work by "+name+". Fixed our roof in one day!", "Lisa P.", areas[0]),
        ("Professional and fair pricing. Highly recommend!", "James M.", areas[1] if len(areas)>1 else areas[0]),
        ("Great work, used them twice. Highly recommend!", "Sarah T.", areas[2] if len(areas)>2 else areas[0]),
    ]
    for text, author, loc in tests:
        t = TESTIMONIAL.replace("TEXT", text).replace("NAME", author).replace("LOC", loc)
        t = t.replace("STARS", "★"*5)
        tc += t
    
    nav = '<a href="#services">Services</a><a href="#areas">Areas</a><a href="#reviews">Reviews</a>'
    
    html = '''<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>'''+name+''' — '''+biz_type.title()+''' Specialists</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Inter,sans-serif;background:#fff;color:#1a1a2e;line-height:1.6}
.container{max-width:1100px;margin:0 auto;padding:0 20px}
nav{background:#1a1a2e;padding:16px 0;position:sticky;top:0;z-index:100}
nav .container{display:flex;justify-content:space-between;align-items:center}
nav .logo{color:#fff;font-size:20px;font-weight:800;text-decoration:none}
nav .logo span{color:#f59e0b}
nav a{color:#94a3b8;text-decoration:none;margin-left:20px;font-size:14px}
nav .cta{background:#f59e0b;color:#1a1a2e;padding:8px 18px;border-radius:8px;font-weight:700}
.hero{background:linear-gradient(135deg,#1a1a2e,#16213e);color:#fff;padding:80px 0;text-align:center}
.hero h1{font-size:42px;font-weight:800;margin-bottom:16px}
.hero h1 span{color:#f59e0b}
.hero p{font-size:18px;color:#94a3b8;max-width:600px;margin:0 auto 32px}
.hero .btn{display:inline-block;background:#f59e0b;color:#1a1a2e;padding:14px 32px;border-radius:10px;font-weight:700;text-decoration:none;margin:0 8px}
.hero .btn-outline{background:transparent;border:2px solid #f59e0b;color:#f59e0b}
.hero .badge{display:inline-block;background:rgba(245,158,11,0.15);color:#f59e0b;padding:6px 16px;border-radius:20px;font-size:13px;margin-bottom:20px}
section{padding:60px 0}
section h2{font-size:28px;font-weight:800;text-align:center;margin-bottom:40px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px}
.card{background:#f8fafc;border-radius:12px;padding:24px;border:1px solid #e2e8f0}
.card h3{font-size:18px;font-weight:700}
.card p{color:#64748b;font-size:14px;margin-top:8px}
.card .price{display:inline-block;margin-top:12px;background:#f59e0b;color:#1a1a2e;padding:4px 12px;border-radius:8px;font-size:13px;font-weight:700}
.areas{display:flex;flex-wrap:wrap;gap:8px;justify-content:center}
.areas span{background:#f1f5f9;padding:8px 16px;border-radius:20px;font-size:14px;font-weight:500}
.testimonials{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px}
.testimonial{background:#f8fafc;border-radius:12px;padding:24px;border:1px solid #e2e8f0}
.testimonial .stars{color:#f59e0b;font-size:18px}
.testimonial p{color:#475569;font-size:14px;font-style:italic;margin:8px 0}
.testimonial .author{font-weight:700;font-size:14px}
.contact{background:#1a1a2e;color:#fff}
.contact h2{color:#fff}
.contact-info{text-align:center;font-size:16px}
.contact-info p{margin:8px 0;color:#94a3b8}
.contact-info strong{color:#f59e0b}
footer{background:#0f172a;color:#64748b;text-align:center;padding:24px;font-size:13px}
@media(max-width:768px){.hero h1{font-size:28px}}
</style>
</head>
<body>
<nav><div class="container"><a href="#" class="logo">'''+emoji+''' <span>'''+name+'''</span></a><div>'''+nav+'''<a href="#contact" class="cta">Get a Quote</a></div></div></nav>
<section class="hero"><div class="container"><div class="badge">⭐ 4.9 — Serving '''+area_short+'''</div><h1>Your '''+biz_type.title()+'''. <span>Done Right.</span></h1><p>'''+name+''' delivers quality '''+biz_type+''' services across '''+area_short+'''. Free quotes, same-day service.</p><a href="tel:'''+phone_raw+'''" class="btn">📞 Call '''+phone+'''</a><a href="#contact" class="btn btn-outline">Free Quote</a></div></section>
<section id="services"><div class="container"><h2>Our Services</h2><div class="cards">'''+sc+'''</div></div></section>
<section id="areas" style="background:#f8fafc"><div class="container"><h2>Service Areas</h2><div class="areas">'''+ab+'''</div><p style="text-align:center;margin-top:16px;color:#64748b">Not sure? <a href="#contact" style="color:#f59e0b">Call us</a></p></div></section>
<section id="reviews"><div class="container"><h2>What Our Customers Say</h2><div class="testimonials">'''+tc+'''</div></div></section>
<section class="contact" id="contact"><div class="container"><h2>Get in Touch</h2><div class="contact-info"><p>📞 <strong>'''+phone+'''</strong></p><p>✉️ '''+email+'''</p><p>🕐 Mon–Fri 7am–5pm, Sat 8am–12pm</p><p style="margin-top:20px;font-size:14px;color:#64748b">Free quotes • Licensed & Insured • 15+ years</p><a href="tel:'''+phone_raw+'''" class="btn" style="display:inline-block;margin-top:20px">Call Now</a></div></div></section>
<footer><p>© '''+str(datetime.now().year)+''' '''+name+'''. All rights reserved. ABN: 12 345 678 901</p></footer>
<script src="https://localflow-backend.up.railway.app/widget.js?business_id='''+bid+'''"></script>
</body>
</html>'''

    site_dir = os.path.join(output_dir, bid)
    os.makedirs(site_dir, exist_ok=True)
    with open(os.path.join(site_dir, "index.html"), "w") as f:
        f.write(html.replace("</div>", "</div>\n"))
    
    print("Site generated for " + name)
    print("  Location: " + site_dir + "/index.html")
    print("  Services: " + str(len(services)) + ", Areas: " + str(len(areas)))
    print("  AI Widget: included")
    
    if serve:
        port = 5180
        subprocess.Popen(["python3", "-m", "http.server", str(port)], cwd=site_dir)
        print("  Dev server: http://localhost:" + str(port))

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Generate a tradie website")
    p.add_argument("--name", required=True)
    p.add_argument("--type", default="roofing")
    p.add_argument("--phone", default="1300 000 000")
    p.add_argument("--email", default="info@business.com.au")
    p.add_argument("--services", default="Roof Repair:550,Roof Replacement:8500,Gutter Cleaning:220,Roof Inspection:150")
    p.add_argument("--areas", default="Parramatta,Hornsby,Castle Hill")
    p.add_argument("--output", default="/home/team/shared/localflow/generated")
    p.add_argument("--serve", action="store_true")
    args = p.parse_args()
    gen(args.name, args.type, args.phone, args.email, args.areas, args.services, args.output, args.serve)/home/engine/.bashrc: line 1: syntax error near unexpected token `('
/home/engine/.bashrc: line 1: `. /etc/profile.d/workload-containment.shn# ~/.bashrc: executed by bash(1) for non-login shells.'
/home/engine/.bashrc: line 1: syntax error near unexpected token `('
/home/engine/.bashrc: line 1: `. /etc/profile.d/workload-containment.shn# ~/.bashrc: executed by bash(1) for non-login shells.'
/home/engine/.bashrc: line 1: syntax error near unexpected token `('
/home/engine/.bashrc: line 1: `. /etc/profile.d/workload-containment.shn# ~/.bashrc: executed by bash(1) for non-login shells.'
