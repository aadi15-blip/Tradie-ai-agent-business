#!/usr/bin/env python3
"""LocalFlow Auto-Deploy — generate a tradie site and deploy to Netlify in one click.

Usage:
  python3 deploy.py --name "Mick's Roofing" --type roofing --phone "1300 555 123" \\
    --areas "Parramatta,Hornsby" --services "Roof Repair:550,Roof Replacement:8500" \\
    --site-name "micks-roofing"

Requires NETLIFY_AUTH_TOKEN env var (get from https://app.netlify.com/user/applications#personal-access-tokens)
"""
import argparse, os, sys, json, io, tarfile, requests

# Add backend to path for database access
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from generator.generate_site import generate_site

NETLIFY_API = "https://api.netlify.com/api/v1"


def deploy_to_netlify(site_dir: str, site_name: str, token: str) -> str:
    """Deploy a static site folder to Netlify and return the live URL."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Step 1: Create a new Netlify site
    print(f"  Creating Netlify site: {site_name}...")
    resp = requests.post(
        f"{NETLIFY_API}/sites",
        headers=headers,
        json={"name": site_name, "force_ssl": True},
    )
    if resp.status_code != 201:
        raise Exception(f"Failed to create site: {resp.status_code} {resp.text}")
    site_data = resp.json()
    site_id = site_data["id"]
    site_url = site_data["ssl_url"] or site_data["url"]
    print(f"  Site created: {site_url}")

    # Step 2: Create a tarball of the site files
    print(f"  Uploading files...")
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for root, dirs, files in os.walk(site_dir):
            for f in files:
                filepath = os.path.join(root, f)
                arcname = os.path.relpath(filepath, site_dir)
                tar.add(filepath, arcname=arcname)
    buf.seek(0)

    # Step 3: Deploy the tarball
    deploy_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/gzip",
    }
    resp = requests.post(
        f"{NETLIFY_API}/sites/{site_id}/deploys",
        headers=deploy_headers,
        data=buf.read(),
    )
    if resp.status_code not in (200, 201):
        raise Exception(f"Failed to deploy: {resp.status_code} {resp.text}")

    print(f"  ✅ Live at: {site_url}")
    return site_url


def main():
    parser = argparse.ArgumentParser(description="Generate + deploy a tradie site")
    parser.add_argument("--name", required=True, help="Business name")
    parser.add_argument("--type", default="roofing", help="Business type")
    parser.add_argument("--phone", default="1300 000 000", help="Phone")
    parser.add_argument("--email", default="info@business.com.au", help="Email")
    parser.add_argument("--services", default="Roof Repair:550,Roof Replacement:8500,Gutter Cleaning:220,Roof Inspection:150", help="Service:Price,Service:Price")
    parser.add_argument("--areas", default="Parramatta,Hornsby,Castle Hill", help="Service areas")
    parser.add_argument("--site-name", help="Netlify subdomain (optional, auto-generated)")
    parser.add_argument("--output", default="/home/team/shared/localflow/generated", help="Output dir")
    args = parser.parse_args()

    token = os.environ.get("NETLIFY_AUTH_TOKEN")
    if not token:
        print("❌ NETLIFY_AUTH_TOKEN not set!")
        print("   Get one from: https://app.netlify.com/user/applications#personal-access-tokens")
        print("   Then: export NETLIFY_AUTH_TOKEN=your_token_here")
        sys.exit(1)

    biz_id = args.name.lower().replace("'", "").replace(" ", "-")[:20]
    site_name = args.site_name or biz_id

    # Generate the site
    print(f"\n🏗️  Generating site for {args.name}...")
    site_dir = os.path.join(args.output, biz_id)
    os.makedirs(site_dir, exist_ok=True)

    # Import and run generator
    from generator.generate_site import gen
    gen(args.name, args.type, args.phone, args.email, args.areas, args.services, args.output, serve=False)

    # Deploy to Netlify
    print(f"\n🚀 Deploying {site_name} to Netlify...")
    url = deploy_to_netlify(site_dir, site_name, token)

    # Save the URL in the database for the dashboard
    try:
        from database import _run_sql
        _run_sql(f"UPDATE businesses SET website = '{url}' WHERE id LIKE '%{biz_id}%'")
        print(f"  URL saved to database")
    except:
        pass

    print(f"\n✅ Done! Your site is live at:")
    print(f"   {url}")
    print(f"   AI Chat Widget: included ✓")
    return url


def auto_deploy_from_signup(business_data: dict) -> str:
    """Called automatically when a tradie signs up. business_data contains:
    business_name, business_type, phone, email, services, areas, plan_id, business_id
    """
    name = business_data.get("business_name", "")
    biz_type = business_data.get("business_type", "roofing")
    phone = business_data.get("phone", "")
    email = business_data.get("email", "")
    services = business_data.get("services", "Roof Repair:550")
    areas = business_data.get("areas", "Sydney Metro")
    biz_id = business_data.get("business_id") or name.lower().replace("'", "").replace(" ", "-")[:20]

    site_dir = os.path.join(os.path.dirname(__file__), "..", "generated", biz_id)
    os.makedirs(site_dir, exist_ok=True)

    from generator.generate_site import gen
    gen(name, biz_type, phone, email, areas, services, os.path.join(os.path.dirname(__file__), "..", "generated"), serve=False)

    token = os.environ.get("NETLIFY_AUTH_TOKEN")
    if not token:
        return None

    return deploy_to_netlify(site_dir, biz_id, token)


if __name__ == "__main__":
    main()