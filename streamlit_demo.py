"""
Streamlit Demo — loads output.json and displays monitoring + document data
exactly as aligned in streamlit_app_v2.py (final output preview).

Run:
  streamlit run streamlit_demo.py --server.port 8502
  streamlit run streamlit_demo.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st

SCRIPT_DIR = Path(__file__).parent.absolute()
DEFAULT_JSON_PATH = SCRIPT_DIR / "data" / "output.json"

# Default timeline for demo when JSON has no timeline_strs (oldest first; include document name)
DEFAULT_TIMELINE = [
    "2026-03-02 05:45:09 UTC — Initial capture",
    "2026-03-02 07:04:43 UTC — No changes",
    "2026-03-02 20:04:50 UTC — No changes",
    "2026-03-02 20:05:56 UTC — No changes",
    "2026-03-02 21:04:12 UTC — 23302355969 (E)FNAR1 – Annual Return",
]

# ── CSS (same as streamlit_app_v2.py for monitoring + document) ───────────────
_CSS = """
<style>
.alert-hdr{background:white;padding:18px 28px;border-radius:8px;
  box-shadow:0 2px 8px rgba(0,0,0,.1);margin-bottom:18px;
  display:flex;justify-content:space-between;align-items:center;}
.alert-hdr h1{color:#2563eb;font-size:22px;margin:0}
.breadcrumb{color:#64748b;font-size:13px}
.card{background:white;border-radius:8px;padding:22px;margin-bottom:18px;
  box-shadow:0 2px 8px rgba(0,0,0,.1);}
.section-title{font-size:19px;font-weight:600;margin-bottom:14px;color:#2c3e50}
.dg{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));
  gap:12px;margin:14px 0}
.di{background:#f8fafc;padding:13px;border-radius:8px;border:1px solid #e2e8f0}
.dl{font-size:11px;color:#64748b;font-weight:700;text-transform:uppercase;margin-bottom:5px}
.dv{font-size:14px;color:#2c3e50;font-weight:600}
.fdc{background:linear-gradient(135deg,#667eea18 0%,#764ba218 100%);
  border:2px solid #667eea;border-radius:12px;padding:20px;margin:16px 0}
.fdc h3{color:#667eea;margin-bottom:9px;font-size:17px}
.ff{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));
  gap:7px;margin-top:12px}
.fi{background:white;padding:7px 11px;border-radius:6px;
  font-size:12px;color:#475569;border:1px solid #e2e8f0}
.tl{position:relative;padding-left:26px;margin:16px 0}
.tl::before{content:'';position:absolute;left:6px;top:0;bottom:0;
  width:2px;background:#e2e8f0}
.ti{position:relative;margin-bottom:16px}
.ti::before{content:'';position:absolute;left:-22px;top:4px;
  width:11px;height:11px;border-radius:50%;background:#2563eb;
  border:2px solid white;box-shadow:0 0 0 2px #2563eb}
.ti.cur::before{background:#dc2626;box-shadow:0 0 0 2px #dc2626}
.td{font-size:12px;color:#64748b;font-weight:600;margin-bottom:2px}
.tc{font-size:13px;color:#2c3e50}
.ib{background:#eff6ff;border-left:4px solid #2563eb;padding:12px;margin:12px 0;border-radius:4px}
.db{background:#fee2e2;border-left:4px solid #dc2626;padding:12px;margin:12px 0;border-radius:4px}
.sb{background:#d1fae5;border-left:4px solid #10b981;padding:12px;margin:12px 0;border-radius:4px}
</style>
"""


def _esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _format_detected_display(monitoring: dict) -> str:
    """Format 'Detected' as date only (e.g. 'March 3, 2026') from capture_info or monitoring.detected."""
    cap = monitoring.get("capture_info") or {}
    cur = cap.get("current_capture") or {}
    date_str = (cur.get("date") or "").strip()
    if date_str:
        try:
            from datetime import datetime
            dt = datetime.strptime(date_str, "%d %B %Y")
            return f"{dt.strftime('%B')} {dt.day}, {dt.year}"
        except Exception:
            return date_str
    return (monitoring.get("detected") or "—").strip()


def _format_timeline_date_only(tdate: str) -> str:
    """Return date-only string for timeline display (hide time)."""
    if not tdate or not tdate.strip():
        return tdate
    s = tdate.strip()
    try:
        from datetime import datetime
        if len(s) >= 10 and s[4] == "-" and s[7] == "-":
            dt = datetime.strptime(s[:10], "%Y-%m-%d")
            return dt.strftime("%d %b %Y")
        if " " in s:
            dt = datetime.strptime(s.split()[0], "%Y-%m-%d")
            return dt.strftime("%d %b %Y")
    except Exception:
        pass
    if len(s) >= 10 and s[4] == "-":
        return s[:10]
    return s


def _load_output_json(path: Path | None = None) -> dict[str, Any] | None:
    p = path or DEFAULT_JSON_PATH
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _render_monitoring(monitoring: dict, timeline_strs: list[str]) -> None:
    """Same layout as streamlit_app_v2._render_monitoring_from_output_json."""
    reg_name = monitoring.get("registry") or "Registry"
    company_display = monitoring.get("company_name") or "Company"
    reg_number = monitoring.get("company_registry_number") or ""

    st.markdown(
        '<div class="card" style="border-left:4px solid #0ea5e9">'
        '<div class="section-title">🔍 Alert Details</div>'
        f"<h2 style='margin:16px 0 6px 0;font-size:22px;color:#2c3e50'>{_esc(company_display)}</h2>"
        f"<p style='color:#64748b;margin-bottom:20px'>"
        f"{_esc(reg_name)} Company Registry Number: {_esc(reg_number)}</p>",
        unsafe_allow_html=True,
    )

    priority = (monitoring.get("priority") or "").lower()
    heading = monitoring.get("alert_heading") or ""
    if priority == "high" and heading:
        st.markdown(
            '<div class="db">'
            "<strong>⚠️ HIGH PRIORITY ALERT</strong>"
            f"<p style='margin-top:8px;font-size:14px'>{_esc(heading)}</p>"
            "</div>",
            unsafe_allow_html=True,
        )
    elif heading:
        st.markdown(
            f'<div class="ib" style="margin-top:0"><strong>Alert</strong><p style="margin-top:6px;font-size:14px;color:#2c3e50">{_esc(heading)}</p></div>',
            unsafe_allow_html=True,
        )

    form_filed = monitoring.get("form_filed") or "—"
    filing_date = monitoring.get("filing_date") or "—"
    detected = _format_detected_display(monitoring)
    data_freshness = monitoring.get("data_freshness") or "—"
    if not filing_date:
        nd = monitoring.get("new_document") or {}
        filing_date = nd.get("made_up_to_date") or "—"

    grid_html = (
        '<div class="dg">'
        f'<div class="di"><div class="dl">Form filed</div><div class="dv">{_esc(form_filed)}</div></div>'
        f'<div class="di"><div class="dl">Filing date</div><div class="dv">{_esc(filing_date)}</div></div>'
        f'<div class="di"><div class="dl">Detected</div><div class="dv">{_esc(detected)}</div></div>'
        f'<div class="di"><div class="dl">Data freshness</div><div class="dv" style="color:#10b981">{_esc(data_freshness)}</div></div>'
        "</div>"
    )
    st.markdown(grid_html, unsafe_allow_html=True)

    new_doc = monitoring.get("new_document") or {}
    form_title = new_doc.get("document_type") or (f"Form {form_filed}" if form_filed != "—" else "Form")
    form_description = monitoring.get("form_description") or new_doc.get("filing_nature") or "—"
    why_matters = monitoring.get("why_this_matters") or new_doc.get("why_to_purchase") or ""

    st.markdown(
        '<div class="fdc" style="margin-top:20px">'
        f"<h3>📋 {_esc(form_title)}</h3>"
        f"<p style='color:#64748b;margin-bottom:12px'>{_esc(form_description)}</p>",
        unsafe_allow_html=True,
    )
    if why_matters:
        st.markdown(
            f'<div class="ib" style="background:#fff;border-left:4px solid #10b981"><strong>Why this matters</strong><p style="margin-top:6px;font-size:14px;color:#64748b">{_esc(why_matters)}</p></div>',
            unsafe_allow_html=True,
        )

    expected_pts = monitoring.get("expected_data_points") or []
    if expected_pts:
        st.markdown("<h4 style='margin:16px 0 10px 0;font-size:15px'>Expected data points for this document type</h4>", unsafe_allow_html=True)
        ff_html = '<div class="ff">'
        for item in expected_pts:
            label = item if isinstance(item, str) else item.get("field", str(item))
            ff_html += f'<div class="fi">✓ {_esc(label)}</div>'
        ff_html += "</div>"
        st.markdown(ff_html, unsafe_allow_html=True)

    rec = monitoring.get("document_purchase_recommendation") or {}
    rec_yes = rec.get("recommendation", "YES").upper() if rec else "YES"
    rec_just = rec.get("justification") or new_doc.get("value_it_provides") or ""
    if rec_yes == "YES" or monitoring.get("has_changes"):
        st.markdown(
            '<div class="sb" style="margin-top:16px">'
            "<strong>💰 Document purchase recommendation: YES</strong>"
            f"<p style='margin-top:6px;font-size:14px'>{_esc(rec_just)}</p>"
            "</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    assessment = monitoring.get("overall_assessment") or ""
    if assessment:
        st.markdown(f'<div class="ib" style="margin-top:12px"><strong>Overall assessment</strong><p style="margin-top:6px;font-size:14px">{_esc(assessment)}</p></div>', unsafe_allow_html=True)

    # if timeline_strs:
    #     st.markdown("<h4 style='margin:20px 0 12px 0;font-size:16px'>Capture timeline</h4>", unsafe_allow_html=True)
    #     tl_html = '<div class="tl">'
    #     displayed = timeline_strs[:10]
    #     for idx, line in enumerate(displayed):
    #         s = str(line).strip()
    #         if " — " in s:
    #             tdate, tcontent = s.split(" — ", 1)
    #             tdate, tcontent = _format_timeline_date_only(tdate.strip()), tcontent.strip()
    #         else:
    #             tdate, tcontent = "", s
    #         is_current = idx == len(displayed) - 1
    #         ti_class = "ti cur" if is_current else "ti"
    #         tl_html += f'<div class="{ti_class}"><div class="td">{_esc(tdate)}</div><div class="tc">{_esc(tcontent)}</div></div>'
    #     tl_html += "</div>"
    #     st.markdown(tl_html, unsafe_allow_html=True)

    previous_filings = monitoring.get("previous_filings") or []
    if previous_filings:
        st.markdown("<h4 style='margin:20px 0 10px 0;font-size:16px'>Previous filings</h4>", unsafe_allow_html=True)
        pf_html = '<div class="tl">'
        for item in previous_filings[:30]:
            if isinstance(item, str):
                pf_html += f'<div class="ti"><div class="tc">{_esc(item)}</div></div>'
            else:
                d = item.get("date", "")
                name = item.get("document_name", "")
                pf_html += f'<div class="ti"><div class="tc">{_esc(d)} {_esc(name)}</div></div>'
        pf_html += "</div>"
        st.markdown(pf_html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_document(doc_section: dict) -> None:
    """Same layout as streamlit_app_v2 document section (Current data + Historical analysis)."""
    st.markdown(
        '<div class="card" style="border-left:4px solid #8b5cf6">'
        '<div class="section-title">📄 Document data</div>'
        "<p style='color:#64748b;margin-bottom:16px'>Current data from latest document and historical comparison.</p>",
        unsafe_allow_html=True,
    )
    current_data = doc_section.get("current_data")
    st.markdown("<h4 style='margin:0 0 10px 0;font-size:16px'>Current data</h4>", unsafe_allow_html=True)
    if isinstance(current_data, list) and current_data:
        content_html = '<div class="ib" style="margin-top:0"><ul style="margin:0 0 10px 0;padding-left:20px;font-size:14px;line-height:1.7;color:#2c3e50">'
        for point in current_data[:50]:
            content_html += f"<li>{_esc(str(point).strip())}</li>"
        content_html += "</ul></div>"
        if len(current_data) > 50:
            content_html += f"<p style='font-size:12px;color:#64748b'>… and {len(current_data) - 50} more points</p>"
        st.markdown(content_html, unsafe_allow_html=True)
    elif isinstance(current_data, str) and current_data.strip():
        blocks = [b.strip() for b in current_data.split("\n\n") if b.strip()]
        if not blocks:
            blocks = [current_data]
        content_html = '<div class="ib" style="margin-top:0"><ul style="margin:0 0 10px 0;padding-left:20px;font-size:14px;line-height:1.7;color:#2c3e50">'
        for blk in blocks[:50]:
            content_html += f"<li>{_esc(blk)}</li>"
        content_html += "</ul></div>"
        if len(blocks) > 50:
            content_html += f"<p style='font-size:12px;color:#64748b'>… and {len(blocks) - 50} more points</p>"
        st.markdown(content_html, unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#64748b;font-size:13px'>—</p>", unsafe_allow_html=True)

    historical = doc_section.get("historical_analysis") or []
    st.markdown("<h4 style='margin:20px 0 10px 0;font-size:16px'>Historical analysis</h4>", unsafe_allow_html=True)
    if historical:
        list_html = '<div class="tl">'
        for point in historical:
            list_html += f'<div class="ti"><div class="tc">{_esc(str(point))}</div></div>'
        list_html += "</div>"
        st.markdown(list_html, unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#64748b;font-size:13px'>—</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    # st.set_page_config(page_title="Alert System", layout="wide", initial_sidebar_state="collapsed")
    st.set_page_config(
        page_title="Alert System",
        page_icon="🔔",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(_CSS, unsafe_allow_html=True)

    data = _load_output_json()
    if not data:
        st.error(f"Could not load output.json from {DEFAULT_JSON_PATH}. Create the file or set path.")
        with st.expander("Expected path"):
            st.code(str(DEFAULT_JSON_PATH))
        return

    monitoring = data.get("monitoring") or {}
    doc_section = data.get("document") or {}
    timeline_strs = monitoring.get("timeline_strs") or data.get("timeline_strs") or DEFAULT_TIMELINE

    # ── Header ─────────────────────────────────────────────────────────────────
    reg_name = monitoring.get("registry") or "Registry"
    company_name = monitoring.get("company_name") or "Company"
    st.markdown(
        '<div class="alert-hdr">'
        "<div><h1>🔔 Alert System</h1></div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ── Monitoring (Alert Details) ───────────────────────────────────────────
    _render_monitoring(monitoring, timeline_strs)

    # ── Document (Current data + Historical analysis) ────────────────────────
    if doc_section:
        st.markdown("---")
        _render_document(doc_section)

    # ── Raw JSON + Download ───────────────────────────────────────────────────
    with st.expander("View raw output.json"):
        st.json(data)
    st.download_button(
        "Download raw JSON",
        data=json.dumps(data, indent=2, ensure_ascii=False),
        file_name="output.json",
        mime="application/json",
        key="download_output_json",
    )


if __name__ == "__main__":
    main()
