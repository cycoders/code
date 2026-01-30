from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uuid
import asyncio

from .config import Config
from .storage import Storage
from .handlers import SignatureVerifier

app = FastAPI(title="Webhook Inspector", docs_url="/docs")

templates = Jinja2Templates(directory="templates")

async def create_app(cfg: Config, storage: Storage) -> FastAPI:
    app.state.cfg = cfg
    app.state.storage = storage

    @app.post("{path:path}")
    async def webhook_handler(path: str, request: Request):
        body = await request.body()
        headers = dict(request.headers)
        req_id = str(uuid.uuid4())[:8]

        # Find endpoint config
        endpoint_cfg = None
        for p, ec in cfg.endpoints.items():
            if request.url.path.startswith(p):
                endpoint_cfg = ec
                break

        verified, provider = SignatureVerifier.detect_and_verify(request, endpoint_cfg.secret if endpoint_cfg else None)

        data = {
            "method": request.method,
            "url": str(request.url),
            "headers": headers,
            "body": body.decode(errors="ignore"),
            "provider": provider,
            "signature_verified": verified,
        }

        storage.save(req_id, data)

        # CLI log via print (uvicorn captures)
        print(f"[bold cyan]POST {path} [{req_id}] {provider}:{'✅' if verified else '❌'} {len(body)}B")

        return {"received": True, "id": req_id, "verified": verified}

    @app.get("/")
    async def dashboard(request: Request):
        recent = storage.list(20)
        return templates.TemplateResponse("index.html", {"request": request, "recent": recent})

    @app.get("/webhook/{req_id}")
    async def detail(req_id: str, request: Request):
        webhook = storage.get(req_id)
        if not webhook:
            raise HTTPException(status_code=404)
        return templates.TemplateResponse("webhook.html", {"request": request, "webhook": webhook})

    return app
