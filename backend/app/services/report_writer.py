from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.core.config import settings
from app.core.redaction import redact_mapping
from app.services.scanner import category_distribution, severity_distribution
class ReportWriter:
    def __init__(self, template_dir: Path | None = None, output_dir: Path | None = None):
        self.template_dir=template_dir or settings.reports_dir/"templates"; self.output_dir=output_dir or settings.reports_dir/"generated"; self.output_dir.mkdir(parents=True, exist_ok=True)
        self.env=Environment(loader=FileSystemLoader(str(self.template_dir)), autoescape=select_autoescape(["html","xml"]))
    def build_context(self, scan: dict[str,Any], findings: list[dict[str,Any]]) -> dict[str,Any]:
        sf=[redact_mapping(f) for f in findings]; ss=redact_mapping(scan)
        return {"scan":ss,"findings":sf,"severity_distribution":severity_distribution(sf),"category_distribution":category_distribution(sf),"failed_findings":[f for f in sf if not f.get("passed")],"authorization_note":"Report covers authorized local/user-owned targets only. It is not a guarantee of security."}
    def write_all(self, scan: dict[str,Any], findings: list[dict[str,Any]], scan_id: str) -> dict[str,str]:
        ctx=self.build_context(scan,findings)
        paths={k:self.output_dir/f"{scan_id}.{ext}" for k,ext in {"json":"json","markdown":"md","html":"html","pdf":"pdf"}.items()}
        paths["json"].write_text(json.dumps(ctx,indent=2, default=str),encoding="utf-8")
        paths["markdown"].write_text(self.env.get_template("report.md.j2").render(**ctx),encoding="utf-8")
        paths["html"].write_text(self.env.get_template("report.html.j2").render(**ctx),encoding="utf-8")
        self._write_pdf(paths["pdf"],ctx)
        return {"json_path":str(paths["json"]),"markdown_path":str(paths["markdown"]),"html_path":str(paths["html"]),"pdf_path":str(paths["pdf"])}
    def _write_pdf(self, path: Path, ctx: dict[str,Any]):
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
        from reportlab.lib import colors
        doc=SimpleDocTemplate(str(path), pagesize=letter, title="LLMShield AI Scan Report"); styles=getSampleStyleSheet()
        story=[Paragraph("LLMShield AI Scan Report",styles["Title"]), Spacer(1,10)]
        scan=ctx["scan"]; story.append(Paragraph(f"Scan ID: {scan.get('id')}",styles["Normal"])); story.append(Paragraph(f"Status: {scan.get('status')} | Risk Score: {scan.get('risk_score')}",styles["Normal"])); story.append(Paragraph(ctx["authorization_note"],styles["Italic"])); story.append(Spacer(1,12))
        table=Table([["Severity","Count"]]+[[k,v] for k,v in ctx["severity_distribution"].items()]); table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.lightgrey),("GRID",(0,0),(-1,-1),0.25,colors.grey)])); story.append(table); story.append(Spacer(1,12))
        for item in ctx["failed_findings"][:30]:
            story.append(Paragraph(f"{item.get('severity','').upper()} — {item.get('test_name')}",styles["Heading3"]))
            story.append(Paragraph(f"Category: {item.get('category')} | Detector: {item.get('detector_name')}",styles["Normal"]))
            story.append(Paragraph(f"Evidence: {str(item.get('evidence',''))[:500]}",styles["Normal"]))
            story.append(Paragraph(f"Mitigation: {str(item.get('mitigation',''))[:700]}",styles["Normal"]))
            story.append(Spacer(1,8))
        doc.build(story)
