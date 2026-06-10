"""LocalFlow — Subscription & signup routes."""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import uuid, subprocess, os

from database import insert, get, list_all, update, now

router = APIRouter(prefix="/api", tags=["Subscriptions"])

def new_id():
    return uuid.uuid4().hex[:12]

@router.get("/plans")
def list_plans():
    return list_all("plans", order_by="price_setup ASC")

@router.post("/signup")
def signup(data: dict):
    name = data.get("business_name", "").strip()
    biz_type = data.get("business_type", "").strip()
    phone = data.get("phone", "").strip()
    email = data.get("email", "").strip()
    plan_id = data.get("plan_id", "starter")
    services_str = data.get("services", "")
    areas_str = data.get("areas", "")

    if not name or not email or not phone:
        raise HTTPException(400, "Business name, email, and phone are required")

    plan = get("plans", plan_id)
    if not plan:
        raise HTTPException(400, "Invalid plan")

    biz_id = new_id()
    insert("businesses", {
        "id": biz_id, "name": name, "type": biz_type,
        "phone": phone, "email": email,
        "services": services_str, "service_areas": areas_str,
        "created_at": now(), "updated_at": now(),
    })

    trial_start = datetime.utcnow()
    trial_end = trial_start + timedelta(days=14)
    sub_id = new_id()
    insert("subscriptions", {
        "id": sub_id, "business_id": biz_id, "plan_id": plan_id,
        "status": "trial",
        "trial_start": trial_start.strftime("%Y-%m-%d %H:%M:%S"),
        "trial_end": trial_end.strftime("%Y-%m-%d %H:%M:%S"),
        "created_at": now(), "updated_at": now(),
    })

    # Auto-generate site + deploy to Netlify
    site_url = None
    if plan_id in ("starter", "pro", "multi"):
        try:
            import subprocess, os
            gen_script = "/home/team/shared/localflow/generator/generate-site.py"
            deploy_script = "/home/team/shared/localflow/generator/deploy.py"
            out_dir = "/home/team/shared/localflow/generated"
            cmd = ["python3", gen_script, "--name", name, "--type", biz_type,
                   "--phone", phone, "--email", email,
                   "--services", services_str or "Roof Repair:550",
                   "--areas", areas_str or "Sydney Metro", "--output", out_dir]
            subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            bid = name.lower().replace("'", "").replace(" ", "-")[:20]
            site_url = f"/generated/{bid}/"
            # Try auto-deploy if Netlify token is set
            if os.environ.get("NETLIFY_AUTH_TOKEN"):
                try:
                    result = subprocess.run(["python3", deploy_script, "--name", name,
                        "--type", biz_type, "--phone", phone, "--email", email,
                        "--services", services_str, "--areas", areas_str,
                        "--site-name", bid], capture_output=True, text=True, timeout=60)
                    if result.returncode == 0:
                        for line in result.stdout.split("\n"):
                            if "https://" in line and ".netlify.app" in line:
                                site_url = line.strip()
                except Exception as e:
                    print(f"Auto-deploy error: {e}")
        except Exception as e:
            print(f"Site gen error: {e}")

    return {
        "business_id": biz_id,
        "subscription_id": sub_id,
        "plan": plan,
        "trial_end": trial_end.strftime("%Y-%m-%d"),
        "status": "trial",
        "site_url": site_url,
        "message": "Welcome to LocalFlow! Your 14-day free trial starts now. Check your email for next steps.",
    }

@router.get("/subscription/{business_id}")
def get_subscription(business_id: str):
    subs = list_all("subscriptions", where=f"business_id = '{business_id}'", limit=1)
    if not subs:
        raise HTTPException(404, "No subscription found")
    sub = subs[0]
    plan = get("plans", sub["plan_id"])
    biz = get("businesses", business_id)
    return {"subscription": sub, "plan": plan, "business": biz}

@router.get("/businesses")
def list_businesses():
    return list_all("businesses", order_by="created_at DESC")

@router.get("/businesses/{business_id}")
def get_business(business_id: str):
    biz = get("businesses", business_id)
    if not biz:
        raise HTTPException(404, "Business not found")
    return biz

@router.put("/businesses/{business_id}")
def update_business(business_id: str, data: dict):
    biz = get("businesses", business_id)
    if not biz:
        raise HTTPException(404, "Business not found")
    allowed = ["name", "type", "phone", "email", "about", "services", "service_areas",
               "hours", "emergency_hours", "license", "abn", "warranty", "insurance",
               "rating", "years_exp", "logo_url", "website"]
    updates = {k: v for k, v in data.items() if k in allowed and v is not None}
    if updates:
        updates["updated_at"] = now()
        update("businesses", business_id, updates)
    return get("businesses", business_id)
