"""
LocalFlow — FastAPI Application Entry Point.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from routes import (
    leads, conversations, bookings, estimates, calendar,
    content, dashboard, chat, subscriptions,
)

app = FastAPI(title="LocalFlow API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health(): return {"status": "healthy", "service": "LocalFlow API", "version": "0.2.0"}

@app.get("/api/health")
def api_health(): return {"status": "ok"}

# Register routers
app.include_router(leads.router)
app.include_router(conversations.router)
app.include_router(bookings.router)
app.include_router(estimates.router)
app.include_router(calendar.router)
app.include_router(content.router)
app.include_router(dashboard.router)
app.include_router(chat.router)
app.include_router(subscriptions.router)

# Widget script endpoint
@app.get("/widget.js", response_class=HTMLResponse)
def widget_js(business_id: str = "demo", api_url: str = "https://localflow-backend.up.railway.app"):
    from widget.widget_builder import generate_widget_script
    return generate_widget_script(business_id, api_url)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8200, reload=True)
