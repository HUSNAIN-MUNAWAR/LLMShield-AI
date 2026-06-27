from __future__ import annotations

from pydantic import BaseModel


class ReportGenerateResponse(BaseModel):
    scan_id: str
    json_path: str
    markdown_path: str
    html_path: str
