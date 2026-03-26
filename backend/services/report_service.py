# backend/services/report_service.py
from services import supabase
from datetime import datetime, timedelta
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# ── Colour palette (matches your dark UI) ─────────────────────────────────────
BLUE      = colors.HexColor('#0055FF')
DARK_BG   = colors.HexColor('#0F172A')
CARD_BG   = colors.HexColor('#1E293B')
BORDER    = colors.HexColor('#334155')
TEXT_MAIN = colors.HexColor('#E2E8F0')
TEXT_SUB  = colors.HexColor('#94A3B8')
GREEN     = colors.HexColor('#10b981')
RED       = colors.HexColor('#ef4444')
ORANGE    = colors.HexColor('#f59e0b')
YELLOW    = colors.HexColor('#eab308')
WHITE     = colors.white

PRIORITY_COLORS = {
    'critical': colors.HexColor('#ef4444'),
    'high':     colors.HexColor('#f59e0b'),
    'medium':   colors.HexColor('#eab308'),
    'low':      colors.HexColor('#10b981'),
}

# ── Styles ────────────────────────────────────────────────────────────────────
def _styles():
    return {
        'title': ParagraphStyle(
            'title', fontName='Helvetica-Bold', fontSize=22,
            textColor=WHITE, alignment=TA_LEFT, spaceAfter=4,
        ),
        'subtitle': ParagraphStyle(
            'subtitle', fontName='Helvetica', fontSize=10,
            textColor=TEXT_SUB, alignment=TA_LEFT, spaceAfter=2,
        ),
        'section': ParagraphStyle(
            'section', fontName='Helvetica-Bold', fontSize=13,
            textColor=WHITE, spaceBefore=18, spaceAfter=8,
        ),
        'label': ParagraphStyle(
            'label', fontName='Helvetica-Bold', fontSize=9,
            textColor=TEXT_SUB, spaceAfter=2,
        ),
        'value': ParagraphStyle(
            'value', fontName='Helvetica-Bold', fontSize=26,
            textColor=WHITE, spaceAfter=2,
        ),
        'normal': ParagraphStyle(
            'normal', fontName='Helvetica', fontSize=9,
            textColor=TEXT_MAIN, spaceAfter=4,
        ),
        'small': ParagraphStyle(
            'small', fontName='Helvetica', fontSize=8,
            textColor=TEXT_SUB,
        ),
        'center': ParagraphStyle(
            'center', fontName='Helvetica', fontSize=9,
            textColor=TEXT_MAIN, alignment=TA_CENTER,
        ),
        'badge_critical': ParagraphStyle(
            'badge_critical', fontName='Helvetica-Bold', fontSize=8,
            textColor=colors.HexColor('#ef4444'), alignment=TA_CENTER,
        ),
        'badge_high': ParagraphStyle(
            'badge_high', fontName='Helvetica-Bold', fontSize=8,
            textColor=colors.HexColor('#f59e0b'), alignment=TA_CENTER,
        ),
        'badge_medium': ParagraphStyle(
            'badge_medium', fontName='Helvetica-Bold', fontSize=8,
            textColor=colors.HexColor('#eab308'), alignment=TA_CENTER,
        ),
        'badge_low': ParagraphStyle(
            'badge_low', fontName='Helvetica-Bold', fontSize=8,
            textColor=colors.HexColor('#10b981'), alignment=TA_CENTER,
        ),
        'right': ParagraphStyle(
            'right', fontName='Helvetica', fontSize=9,
            textColor=TEXT_MAIN, alignment=TA_RIGHT,
        ),
    }


# ── Data aggregation ──────────────────────────────────────────────────────────

def _get_start_date(range_str: str) -> datetime:
    if range_str == 'weekly':
        return datetime.utcnow() - timedelta(days=7)
    return datetime.utcnow() - timedelta(days=30)


def aggregate_report_data(user_id: str, role: str, range_str: str) -> dict:
    """Pull all metrics needed for the report from Supabase."""
    start_date = _get_start_date(range_str)
    start_iso  = start_date.isoformat()

    # ── Incidents ──────────────────────────────────────────────────────────────
    inc_query = supabase.table("incidents").select("*").gte("created_at", start_iso)

    # Responders only see incidents linked to their resource type via incident_resources
    if role != 'admin':
        # Get resource IDs belonging to this user's type
        res_resp = (
            supabase.table("resources")
            .select("id")
            .eq("type", role)
            .execute()
        )
        resource_ids = [r['id'] for r in (res_resp.data or [])]

        if resource_ids:
            ir_resp = (
                supabase.table("incident_resources")
                .select("incident_id")
                .in_("resource_id", resource_ids)
                .execute()
            )
            incident_ids = list({r['incident_id'] for r in (ir_resp.data or [])})
        else:
            incident_ids = []

        if not incident_ids:
            incidents = []
        else:
            inc_resp = inc_query.in_("id", incident_ids).execute()
            incidents = inc_resp.data or []
    else:
        inc_resp  = inc_query.order("created_at", desc=True).execute()
        incidents = inc_resp.data or []

    total     = len(incidents)
    open_     = sum(1 for i in incidents if i['status'] == 'open')
    in_prog   = sum(1 for i in incidents if i['status'] == 'in_progress')
    closed    = sum(1 for i in incidents if i['status'] == 'closed')

    priorities = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    for i in incidents:
        p = (i.get('priority') or '').lower()
        if p in priorities:
            priorities[p] += 1

    # ── Response times ─────────────────────────────────────────────────────────
    response_times = []
    for i in incidents:
        if i.get('created_at') and i.get('updated_at') and i['status'] == 'closed':
            try:
                created = datetime.fromisoformat(i['created_at'].replace('Z', '+00:00'))
                updated = datetime.fromisoformat(i['updated_at'].replace('Z', '+00:00'))
                diff_min = (updated - created).total_seconds() / 60
                if diff_min > 0:
                    response_times.append(diff_min)
            except Exception:
                pass

    avg_response   = round(sum(response_times) / len(response_times), 1) if response_times else 0
    fastest        = round(min(response_times), 1) if response_times else 0
    slowest        = round(max(response_times), 1) if response_times else 0

    # ── Resources ──────────────────────────────────────────────────────────────
    if role == 'admin':
        res_resp = supabase.table("resources").select("*").execute()
        resources = res_resp.data or []
    else:
        res_resp  = supabase.table("resources").select("*").eq("type", role).execute()
        resources = res_resp.data or []

    res_total     = len(resources)
    res_available = sum(1 for r in resources if r['status'] == 'available')
    res_busy      = sum(1 for r in resources if r['status'] == 'busy')
    util_pct      = round((res_busy / res_total * 100), 1) if res_total else 0

    # ── Incident resources (responders per incident) ───────────────────────────
    incident_ids_list = [i['id'] for i in incidents]
    avg_responders = 0
    if incident_ids_list:
        ir_resp = (
            supabase.table("incident_resources")
            .select("incident_id")
            .in_("incident_id", incident_ids_list)
            .execute()
        )
        ir_data = ir_resp.data or []
        if ir_data and total:
            avg_responders = round(len(ir_data) / total, 1)

    # ── Calls ──────────────────────────────────────────────────────────────────
    calls_data   = []
    if incident_ids_list:
        calls_resp = (
            supabase.table("call_logs")
            .select("*")
            .in_("incident_id", incident_ids_list)
            .execute()
        )
        calls_data = calls_resp.data or []

    total_calls   = len(calls_data)
    confirmed     = sum(1 for c in calls_data if c.get('status') == 'confirmed')
    no_answer     = sum(1 for c in calls_data if c.get('status') == 'no-answer')
    call_success  = round((confirmed / total_calls * 100), 1) if total_calls else 0

    # ── Recent incidents (last 10) for table ───────────────────────────────────
    recent = sorted(incidents, key=lambda x: x.get('created_at', ''), reverse=True)[:10]

    return {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "range":        range_str,
        "role":         role,
        "incidents": {
            "total":       total,
            "open":        open_,
            "in_progress": in_prog,
            "closed":      closed,
            "priorities":  priorities,
        },
        "performance": {
            "avg_response_min": avg_response,
            "fastest_min":      fastest,
            "slowest_min":      slowest,
        },
        "resources": {
            "total":           res_total,
            "available":       res_available,
            "busy":            res_busy,
            "utilization_pct": util_pct,
            "avg_per_incident": avg_responders,
        },
        "calls": {
            "total":        total_calls,
            "confirmed":    confirmed,
            "no_answer":    no_answer,
            "success_rate": call_success,
        },
        "recent_incidents": recent,
    }


# ── PDF generation ────────────────────────────────────────────────────────────

def _dark_table_style(extra=None):
    base = [
        ('BACKGROUND',   (0, 0), (-1, 0),  CARD_BG),
        ('TEXTCOLOR',    (0, 0), (-1, 0),  TEXT_SUB),
        ('FONTNAME',     (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1, 0),  8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [DARK_BG, colors.HexColor('#111827')]),
        ('TEXTCOLOR',    (0, 1), (-1, -1), TEXT_MAIN),
        ('FONTNAME',     (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',     (0, 1), (-1, -1), 8),
        ('GRID',         (0, 0), (-1, -1), 0.3, BORDER),
        ('ROWPADDING',   (0, 0), (-1, -1), 6),
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
    ]
    if extra:
        base.extend(extra)
    return TableStyle(base)


def _stat_block(label: str, value: str, sub: str, color, styles: dict):
    """Returns a 1-cell table acting as a stat card."""
    inner = Table([
        [Paragraph(label, styles['label'])],
        [Paragraph(value, ParagraphStyle('v', fontName='Helvetica-Bold', fontSize=22,
                                         textColor=color, spaceAfter=2))],
        [Paragraph(sub,   styles['small'])],
    ], colWidths=[None])
    inner.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, -1), CARD_BG),
        ('BOX',         (0, 0), (-1, -1), 0.5, BORDER),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING',  (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('ROUNDEDCORNERS', [6]),
    ]))
    return inner


def generate_pdf_report(data: dict, reporter_name: str) -> bytes:
    """Build the PDF and return raw bytes."""
    buf    = BytesIO()
    W, H   = A4
    margin = 18 * mm

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=margin, rightMargin=margin,
        topMargin=margin,  bottomMargin=margin,
    )

    S     = _styles()
    story = []
    cw    = W - 2 * margin   # usable column width

    # ── Cover header ──────────────────────────────────────────────────────────
    range_label = 'Weekly Report' if data['range'] == 'weekly' else 'Monthly Report'
    role_label  = data['role'].replace('_', ' ').title()
    scope_label = 'Platform-Wide' if data['role'] == 'admin' else f'{role_label} Unit'

    header_data = [[
        Paragraph(f"<b>ResQNet</b> — {range_label}", S['title']),
        Paragraph(data['generated_at'], ParagraphStyle(
            'gr', fontName='Helvetica', fontSize=8,
            textColor=TEXT_SUB, alignment=TA_RIGHT)),
    ]]
  
 

    story.append(Paragraph(
        f"Scope: <b>{scope_label}</b> &nbsp;|&nbsp; Prepared by: <b>{reporter_name}</b>",
        S['subtitle']
    ))
    story.append(Spacer(1, 10))

    # ── Section: Incident Overview ────────────────────────────────────────────
    story.append(Paragraph("Incident Overview", S['section']))

    inc = data['incidents']
    card_w = (cw - 9) / 4

    inc_cards = Table([[
        _stat_block("TOTAL",       str(inc['total']),       "all incidents",          BLUE,   S),
        _stat_block("OPEN",        str(inc['open']),         "awaiting response",      ORANGE, S),
        _stat_block("IN PROGRESS", str(inc['in_progress']), "currently active",       YELLOW, S),
        _stat_block("CLOSED",      str(inc['closed']),      "successfully resolved",  GREEN,  S),
    ]], colWidths=[card_w] * 4, hAlign='LEFT')
    inc_cards.setStyle(TableStyle([('LEFTPADDING', (0,0),(-1,-1), 0),
                                    ('RIGHTPADDING',(0,0),(-1,-1), 3)]))
    story.append(inc_cards)
    story.append(Spacer(1, 14))

    # Priority distribution table
    story.append(Paragraph("Priority Distribution", S['label']))
    pri = inc['priorities']
    total_inc = inc['total'] or 1

    def pct_bar(count, total, col):
        pct = round(count / total * 100)
        bar = '█' * (pct // 5) + '░' * (20 - pct // 5)
        return f"{bar}  {pct}%"

    pri_rows = [
        [Paragraph('PRIORITY', S['label']), Paragraph('COUNT', S['label']),
         Paragraph('SHARE', S['label']), Paragraph('', S['label'])],
    ]
    for name, key, col in [
        ('Critical', 'critical', colors.HexColor('#ef4444')),
        ('High',     'high',     colors.HexColor('#f59e0b')),
        ('Medium',   'medium',   colors.HexColor('#eab308')),
        ('Low',      'low',      colors.HexColor('#10b981')),
    ]:
        count = pri.get(key, 0)
        pri_rows.append([
            Paragraph(name, ParagraphStyle('pn', fontName='Helvetica-Bold',
                                            fontSize=9, textColor=col)),
            Paragraph(str(count), S['normal']),
            Paragraph(f"{round(count/total_inc*100)}%", S['normal']),
            Paragraph(pct_bar(count, total_inc, col),
                      ParagraphStyle('bar', fontName='Courier', fontSize=7,
                                     textColor=col)),
        ])

    pri_tbl = Table(pri_rows, colWidths=[cw*0.2, cw*0.12, cw*0.1, cw*0.58])
    pri_tbl.setStyle(_dark_table_style())
    story.append(pri_tbl)
    story.append(Spacer(1, 14))

    # ── Section: Performance ──────────────────────────────────────────────────
    story.append(HRFlowable(width=cw, thickness=0.5, color=BORDER))
    story.append(Paragraph("Response Performance", S['section']))

    perf = data['performance']
    card_w3 = (cw - 6) / 3

    perf_cards = Table([[
        _stat_block("AVG RESPONSE TIME", f"{perf['avg_response_min']} min",
                    "mean resolution time", BLUE,   S),
        _stat_block("FASTEST",           f"{perf['fastest_min']} min",
                    "quickest response",   GREEN,  S),
        _stat_block("SLOWEST",           f"{perf['slowest_min']} min",
                    "longest response",    RED,    S),
    ]], colWidths=[card_w3] * 3, hAlign='LEFT')
    perf_cards.setStyle(TableStyle([('LEFTPADDING', (0,0),(-1,-1), 0),
                                     ('RIGHTPADDING',(0,0),(-1,-1), 3)]))
    story.append(perf_cards)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Response time is calculated from incident creation to closure (closed incidents only).",
        S['small']
    ))
    story.append(Spacer(1, 14))

    # ── Section: Resources ────────────────────────────────────────────────────
    story.append(HRFlowable(width=cw, thickness=0.5, color=BORDER))
    story.append(Paragraph("Resource Utilization", S['section']))

    res  = data['resources']
    card_w4 = (cw - 9) / 4

    res_cards = Table([[
        _stat_block("TOTAL RESOURCES",   str(res['total']),
                    "registered",         TEXT_MAIN, S),
        _stat_block("AVAILABLE",         str(res['available']),
                    "ready to deploy",    GREEN,     S),
        _stat_block("DEPLOYED",          str(res['busy']),
                    "currently active",   ORANGE,    S),
        _stat_block("UTILIZATION",       f"{res['utilization_pct']}%",
                    f"avg {res['avg_per_incident']} per incident", BLUE, S),
    ]], colWidths=[card_w4] * 4, hAlign='LEFT')
    res_cards.setStyle(TableStyle([('LEFTPADDING', (0,0),(-1,-1), 0),
                                    ('RIGHTPADDING',(0,0),(-1,-1), 3)]))
    story.append(res_cards)
    story.append(Spacer(1, 14))

    # ── Section: Dispatch Calls ───────────────────────────────────────────────
    story.append(HRFlowable(width=cw, thickness=0.5, color=BORDER))
    story.append(Paragraph("Dispatch Call Analytics", S['section']))

    calls    = data['calls']
    card_w4b = (cw - 9) / 4

    call_cards = Table([[
        _stat_block("TOTAL CALLS",   str(calls['total']),
                    "dispatch attempts",  TEXT_MAIN, S),
        _stat_block("CONFIRMED",     str(calls['confirmed']),
                    "responder answered", GREEN,     S),
        _stat_block("NO ANSWER",     str(calls['no_answer']),
                    "missed calls",       RED,       S),
        _stat_block("SUCCESS RATE",  f"{calls['success_rate']}%",
                    "confirmed / total",  BLUE,      S),
    ]], colWidths=[card_w4b] * 4, hAlign='LEFT')
    call_cards.setStyle(TableStyle([('LEFTPADDING', (0,0),(-1,-1), 0),
                                     ('RIGHTPADDING',(0,0),(-1,-1), 3)]))
    story.append(call_cards)
    story.append(Spacer(1, 14))

    # ── Section: Recent Incidents Table ───────────────────────────────────────
    story.append(HRFlowable(width=cw, thickness=0.5, color=BORDER))
    story.append(Paragraph("Recent Incidents", S['section']))

    recent = data['recent_incidents']
    if not recent:
        story.append(Paragraph("No incidents in this period.", S['normal']))
    else:
        rows = [[
            Paragraph('TITLE',    S['label']),
            Paragraph('LOCATION', S['label']),
            Paragraph('PRIORITY', S['label']),
            Paragraph('STATUS',   S['label']),
            Paragraph('DATE',     S['label']),
        ]]
        for inc_row in recent:
            pri_key = (inc_row.get('priority') or 'low').lower()
            pri_col = PRIORITY_COLORS.get(pri_key, TEXT_MAIN)
            status  = (inc_row.get('status') or '').replace('_', ' ').title()
            try:
                dt = datetime.fromisoformat(
                    (inc_row.get('created_at') or '').replace('Z', '+00:00')
                ).strftime('%b %d, %H:%M')
            except Exception:
                dt = inc_row.get('created_at', '')[:10]

            rows.append([
                Paragraph((inc_row.get('title') or '')[:40], S['normal']),
                Paragraph((inc_row.get('location') or '')[:30], S['small']),
                Paragraph((inc_row.get('priority') or '').upper(),
                           ParagraphStyle('pp', fontName='Helvetica-Bold',
                                          fontSize=8, textColor=pri_col)),
                Paragraph(status, S['normal']),
                Paragraph(dt,     S['small']),
            ])

        inc_tbl = Table(rows, colWidths=[cw*0.30, cw*0.22, cw*0.12, cw*0.16, cw*0.20])
        inc_tbl.setStyle(_dark_table_style())
        story.append(inc_tbl)

    story.append(Spacer(1, 20))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width=cw, thickness=0.5, color=BORDER))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"ResQNet Emergency Management System — Confidential — Generated {data['generated_at']}",
        ParagraphStyle('footer', fontName='Helvetica', fontSize=7,
                       textColor=TEXT_SUB, alignment=TA_CENTER)
    ))

    # ── Page background callback ───────────────────────────────────────────────
    def dark_bg(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(DARK_BG)
        canvas.rect(0, 0, W, H, fill=1, stroke=0)
        canvas.restoreState()

    doc.build(story, onFirstPage=dark_bg, onLaterPages=dark_bg)
    return buf.getvalue()