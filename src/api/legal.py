from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["legal"])

_PRIVACY_POLICY_HTML = (Path(__file__).parent / "privacy_policy.html").read_text(
    encoding="utf-8"
)


@router.get("/privacy", response_class=HTMLResponse, include_in_schema=False)
def privacy_policy() -> HTMLResponse:
    """Public privacy policy page, linked from the app and App Store Connect."""
    return HTMLResponse(content=_PRIVACY_POLICY_HTML)
