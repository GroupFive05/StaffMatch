import html
from collections import defaultdict

TREE_CSS = """
<style>
.ph-tree { font-size: 0.92rem; color: #1E1B4B; }
.ph-tree details { border: 1px solid #ECE6FA; border-radius: 14px; background: #ffffff; margin-bottom: 0.55rem; box-shadow: 0 2px 10px rgba(76,29,149,0.06); }
.ph-tree details details { box-shadow: none; border-radius: 10px; background: #FBFAFF; margin: 0.4rem 0 0 0; }
.ph-tree summary { list-style: none; cursor: pointer; display: flex; align-items: center; gap: 0.7rem; padding: 0.7rem 1rem; }
.ph-tree summary::-webkit-details-marker { display: none; }
.ph-tree summary::before { content: ""; flex: 0 0 8px; height: 8px; border-right: 2px solid #7C3AED; border-bottom: 2px solid #7C3AED; transform: rotate(-45deg); transition: transform 0.15s ease; margin-right: 4px; }
.ph-tree details[open] > summary::before { transform: rotate(45deg); }
.ph-tree .leaf { display: flex; align-items: center; gap: 0.7rem; padding: 0.55rem 1rem 0.55rem 2.1rem; border: 1px solid #ECE6FA; border-radius: 10px; background: #FBFAFF; margin-top: 0.4rem; }
.ph-tree .id { font-weight: 700; color: #5B21B6; min-width: 76px; }
.ph-tree .title { font-weight: 600; flex: 1 1 220px; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ph-tree .muted { color: #6B7280; white-space: nowrap; }
.ph-tree .client { color: #6B7280; flex: 0 1 190px; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ph-tree .period { color: #6B7280; white-space: nowrap; font-size: 0.85rem; }
.ph-tree .metric { background: #F3EEFF; color: #5B21B6; border-radius: 999px; padding: 2px 10px; font-size: 0.78rem; font-weight: 600; white-space: nowrap; }
.ph-tree .total { margin-left: auto; font-weight: 800; font-size: 1rem; white-space: nowrap; min-width: 110px; text-align: right; }
.ph-tree .total small { display: block; font-weight: 500; font-size: 0.7rem; color: #6B7280; }
.ph-tree .badge { border-radius: 999px; padding: 2px 10px; font-size: 0.76rem; font-weight: 600; white-space: nowrap; }
.ph-tree .b-ok { background: #DCFCE7; color: #166534; }
.ph-tree .b-warn { background: #FEF3C7; color: #92400E; }
.ph-tree .b-closed { background: #FEE2E2; color: #991B1B; }
.ph-tree .b-pipe { background: #E0E7FF; color: #3730A3; }
.ph-tree .b-none { background: #F3F4F6; color: #6B7280; }
.ph-tree .body { padding: 0 1rem 0.9rem 2.1rem; }
.ph-tree .meta { color: #6B7280; font-size: 0.84rem; padding: 0 0 0.2rem 0; }
.ph-tree table { width: 100%; border-collapse: collapse; margin-top: 0.5rem; font-size: 0.86rem; }
.ph-tree th { text-align: left; color: #6B7280; font-weight: 600; padding: 6px 8px; border-bottom: 1px solid #ECE6FA; }
.ph-tree td { padding: 6px 8px; border-bottom: 1px solid #F4F0FC; white-space: nowrap; }
.ph-tree td.num, .ph-tree th.num { text-align: right; }
.ph-tree .group-title { font-weight: 800; color: #1E1B4B; margin: 1.2rem 0 0.5rem 0; font-size: 1.05rem; }
.ph-tree .group-note { color: #6B7280; font-size: 0.85rem; margin: -0.3rem 0 0.6rem 0; }
</style>
"""

STATUS_CLASSES = {
    "Active": "b-ok",
    "Won": "b-ok",
    "Rolling-off": "b-warn",
    "Closed": "b-closed",
    "Pipeline": "b-pipe",
    "Open": "b-pipe",
}


def _e(value):
    return html.escape(str(value)) if value not in (None, "") else "—"


def _eur(value):
    try:
        return "€ " + f"{float(value or 0):,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return "—"


def _badge(label):
    css = STATUS_CLASSES.get(label, "b-none")
    return f'<span class="badge {css}">{_e(label)}</span>'


def _period(row):
    return f"{_e(row.get('start_date'))} → {_e(row.get('end_date'))}"


def _resource_name(osr):
    name = f"{osr.get('resource_nome') or ''} {osr.get('resource_cognome') or ''}".strip()
    return name or "Unassigned"


def _osr_table(osr_rows):
    rows = "".join(
        "<tr>"
        f"<td>{_badge(r.get('calculated_status') or 'n/a')}</td>"
        f"<td>{_e(r.get('osr_id'))}</td>"
        f"<td><b>{_e(_resource_name(r))}</b> <span class='muted'>EID {_e(r.get('resource_eid'))}</span></td>"
        f"<td>{_e(r.get('project_role'))}</td>"
        f"<td class='num'>{_e(r.get('allocation_pct'))}%</td>"
        f"<td class='num'>{_e(r.get('chargeability_pct'))}%</td>"
        f"<td>{_period(r)}</td>"
        "</tr>"
        for r in sorted(osr_rows, key=lambda x: (x.get("start_date") or ""), reverse=True)
    )

    return (
        "<table><thead><tr>"
        "<th>Status</th><th>OSR</th><th>Resource</th><th>Project role</th>"
        "<th class='num'>Alloc.</th><th class='num'>Charge.</th><th>Period</th>"
        f"</tr></thead><tbody>{rows}</tbody></table>"
    )


def _opportunity_block(opportunity, osr_rows, expand):
    summary = (
        f'<span class="id">{_e(opportunity.get("opportunity_id"))}</span>'
        f'<span class="title">{_e(opportunity.get("opportunity_title"))}</span>'
        f'<span class="client">{_e(opportunity.get("main_tech_cluster"))}</span>'
        f'{_badge(opportunity.get("opportunity_stage") or "n/a")}'
        f'{_badge(opportunity.get("opportunity_status") or "n/a")}'
        f'<span class="period">{_period(opportunity)}</span>'
        f'<span class="metric">{len(osr_rows)} OSR</span>'
        f'<span class="total">{_eur(opportunity.get("opportunity_value"))}</span>'
    )

    if not osr_rows:
        return (
            f'<div class="leaf">{summary}<span class="badge b-none">No OSR assigned</span></div>'
        )

    return (
        f'<details{" open" if expand else ""}><summary>{summary}</summary>'
        f'<div class="body">{_osr_table(osr_rows)}</div></details>'
    )


def build_tree(data, search="", contract_statuses=(), expand_all=False):
    contracts = sorted(data.get("contracts", []), key=lambda c: str(c.get("contract_id")))
    opportunities = data.get("opportunities", [])
    osr_rows = data.get("osr", [])

    osr_by_opportunity = defaultdict(list)
    for row in osr_rows:
        osr_by_opportunity[row.get("opportunity_id")].append(row)

    opportunities_by_contract = defaultdict(list)
    uncontracted = []
    for opportunity in sorted(opportunities, key=lambda o: str(o.get("opportunity_id"))):
        if opportunity.get("contract_missing") or not opportunity.get("contract_id"):
            uncontracted.append(opportunity)
        else:
            opportunities_by_contract[opportunity["contract_id"]].append(opportunity)

    needle = (search or "").strip().lower()

    def matches(contract, contract_opportunities):
        if not needle:
            return True

        parts = [
            contract.get("contract_id"), contract.get("contract_title"),
            contract.get("client_name"), contract.get("manager_nome"), contract.get("manager_cognome"),
        ]
        for opportunity in contract_opportunities:
            parts += [opportunity.get("opportunity_id"), opportunity.get("opportunity_title")]
            for row in osr_by_opportunity.get(opportunity.get("opportunity_id"), []):
                parts += [_resource_name(row), row.get("resource_eid"), row.get("osr_id"), row.get("project_role")]

        return needle in " ".join(str(p) for p in parts if p).lower()

    stats = {"contracts": 0, "opportunities": 0, "osr": 0, "resources": set(), "total": 0.0}
    blocks = []

    for contract in contracts:
        status = contract.get("contract_status")

        if contract_statuses and status not in contract_statuses:
            continue

        contract_opportunities = opportunities_by_contract.get(contract.get("contract_id"), [])

        if not matches(contract, contract_opportunities):
            continue

        won_total = sum(
            float(o.get("opportunity_value") or 0)
            for o in contract_opportunities if o.get("opportunity_stage") == "Won"
        )
        contract_osr = [
            row for o in contract_opportunities
            for row in osr_by_opportunity.get(o.get("opportunity_id"), [])
        ]
        resources = {row.get("resource_eid") for row in contract_osr}

        stats["contracts"] += 1
        stats["opportunities"] += len(contract_opportunities)
        stats["osr"] += len(contract_osr)
        stats["resources"] |= resources
        stats["total"] += won_total

        revenue = float(contract.get("contract_revenue") or 0)
        mismatch = abs(revenue - won_total) >= 1
        manager = f"{contract.get('manager_nome') or ''} {contract.get('manager_cognome') or ''}".strip()

        meta = " · ".join(
            part for part in (
                f"Manager: {_e(manager)}" if manager else "",
                f"Service group: {_e(contract.get('service_group'))}" if contract.get("service_group") else "",
                f"Industry: {_e(contract.get('industry_sector'))}" if contract.get("industry_sector") else "",
                f"Revenue {_eur(revenue)} · Costs {_eur(contract.get('contract_costs'))} · Margin {_eur(contract.get('contract_margin'))}",
                "⚠ contract revenue differs from the sum of won opportunities" if mismatch else "",
            ) if part
        )

        children = "".join(
            _opportunity_block(o, osr_by_opportunity.get(o.get("opportunity_id"), []), expand_all)
            for o in contract_opportunities
        ) or '<div class="leaf"><span class="muted">No opportunities linked to this contract</span></div>'

        open_attr = " open" if expand_all or (needle and len(contracts) > 0) else ""

        blocks.append(
            f'<details{open_attr}><summary>'
            f'<span class="id">{_e(contract.get("contract_id"))}</span>'
            f'<span class="title">{_e(contract.get("contract_title"))}</span>'
            f'<span class="client">{_e(contract.get("client_name"))}</span>'
            f'{_badge(status or "n/a")}'
            f'<span class="period">{_period(contract)}</span>'
            f'<span class="metric">{len(contract_opportunities)} OPP</span>'
            f'<span class="metric">{len(contract_osr)} OSR</span>'
            f'<span class="metric">{len(resources)} res.</span>'
            f'<span class="total">{_eur(won_total)}<small>won opportunities</small></span>'
            f'</summary><div class="body"><div class="meta">{meta}</div>{children}</div></details>'
        )

    pipeline_block = ""
    visible_uncontracted = [
        o for o in uncontracted
        if not needle or needle in f"{o.get('opportunity_id')} {o.get('opportunity_title')}".lower()
    ]

    if visible_uncontracted and not contract_statuses:
        pipeline_total = sum(float(o.get("opportunity_value") or 0) for o in visible_uncontracted)
        pipeline_block = (
            '<div class="group-title">Pipeline — opportunities not yet contracted</div>'
            f'<div class="group-note">{len(visible_uncontracted)} open opportunities · '
            f'{_eur(pipeline_total)} potential value (not included in contract totals)</div>'
            + "".join(
                _opportunity_block(o, osr_by_opportunity.get(o.get("opportunity_id"), []), expand_all)
                for o in visible_uncontracted
            )
        )

    if not blocks and not pipeline_block:
        body = '<div class="group-note">No contracts match the selected filters.</div>'
    else:
        body = "".join(blocks) + pipeline_block

    stats["resources"] = len(stats["resources"])

    return TREE_CSS + f'<div class="ph-tree">{body}</div>', stats
