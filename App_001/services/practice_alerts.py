"""
Practice Alert: controlli automatici su contratti, opportunity, OSR,
risorse, fatturazione e qualità dei dati.

Ogni controllo è descritto nel CATALOG (area, severità, spiegazione e
azione consigliata) in modo che l'interfaccia sia autoesplicativa.
"""
from datetime import date, timedelta

from services import db

LOW_CHARGEABILITY_PCT = 50

# (code, area, severity, label, description, action)
# I testi possono usare {days} (soglia scadenza) e {charge} (soglia chargeability).
CATALOG = [
    # ── Contratti ─────────────────────────────────────────────────────────────
    ("contract_no_opportunity", "contract", "high",
     "No opportunity",
     "Open contract with no opportunity linked: no work is being planned on it.",
     "Create an opportunity for it in Practice Hub › Data Entry, or close the contract."),
    ("contract_expiring", "contract", "medium",
     "Expiring soon",
     "Open contract whose end date falls within the next {days} days.",
     "Check whether it will be renewed or extended and plan the roll-off of the people on it."),
    ("contract_expired_open", "contract", "high",
     "Expired but still open",
     "The end date has passed but the status is not Closed.",
     "Close the contract or correct its end date."),
    ("contract_negative_margin", "contract", "high",
     "Negative margin",
     "Costs are higher than revenue.",
     "Review costs and revenue with the contract manager."),
    ("contract_no_manager", "contract", "medium",
     "No manager",
     "No contract manager is assigned, or the manager is not among the resources.",
     "Assign a contract manager."),

    # ── Opportunity ───────────────────────────────────────────────────────────
    ("opportunity_no_contract", "opportunity", "high",
     "No contract",
     "Open opportunity not linked to any existing contract.",
     "Link the opportunity to its contract."),
    ("opportunity_no_osr", "opportunity", "medium",
     "No OSR",
     "Open opportunity with no OSR at all: nobody is staffed on it.",
     "Staff it with Match AI or create the OSR in Practice Hub › Data Entry."),
    ("opportunity_no_active_osr", "opportunity", "medium",
     "No active OSR",
     "All its OSR have already ended: nobody is currently staffed on it.",
     "Extend the OSR or staff the opportunity again with Match AI."),
    ("opportunity_expiring", "opportunity", "medium",
     "Expiring soon",
     "Open opportunity whose end date falls within the next {days} days.",
     "Check whether it will be extended and plan the roll-off of the people on it."),
    ("opportunity_expired_open", "opportunity", "high",
     "Expired but still open",
     "The end date has passed but the status is not Closed.",
     "Close the opportunity or correct its end date."),
    ("opportunity_pipeline_late", "opportunity", "medium",
     "Pipeline already started",
     "Still in Pipeline although its start date has already passed.",
     "Update status/stage (Won or Closed) or move the start date."),
    ("opportunity_no_milestone", "opportunity", "medium",
     "No milestones",
     "Active opportunity (not Pipeline) with no billing milestone planned.",
     "Plan the billing milestones."),

    # ── OSR ───────────────────────────────────────────────────────────────────
    ("osr_expiring", "osr", "medium",
     "Expiring soon",
     "Active OSR ending within the next {days} days: the person will soon be free.",
     "Extend the OSR or look for the next assignment with Match AI."),
    ("osr_low_chargeability", "osr", "low",
     "Low chargeability",
     "Active OSR with chargeability below {charge}%.",
     "Check why the person is not chargeable enough on this OSR."),

    # ── Risorse ───────────────────────────────────────────────────────────────
    ("resource_no_osr", "resource", "medium",
     "No OSR at all",
     "The resource has never had an OSR.",
     "Find an assignment with Match AI."),
    ("resource_no_active_osr", "resource", "medium",
     "No active OSR (bench)",
     "All OSR of the resource have ended: the resource is currently free.",
     "Find a new assignment with Match AI."),
    ("resource_over_allocated", "resource", "high",
     "Over-allocated",
     "The sum of active OSR allocations is above 100%.",
     "Reduce an allocation or move the person from one OSR."),
    ("resource_under_allocated", "resource", "low",
     "Partially allocated",
     "Active OSR allocations add up to less than 100%: the person has spare capacity.",
     "Use the remaining capacity with Match AI."),
    ("resource_cert_expiring", "resource", "medium",
     "Certification expiring",
     "A certification expires within the next {days} days.",
     "Plan the renewal."),
    ("resource_cert_expired", "resource", "medium",
     "Certification expired",
     "A certification is already expired.",
     "Renew it or remove it from the profile."),

    # ── Fatturazione ──────────────────────────────────────────────────────────
    ("milestone_overdue", "billing", "high",
     "Overdue billing",
     "Milestone not invoiced and past its planned billing date (or marked Overdue).",
     "Issue the invoice or update the planned billing date."),
    ("milestone_due_soon", "billing", "medium",
     "Billing due soon",
     "Milestone not yet invoiced, planned within the next {days} days.",
     "Prepare the invoice."),

    # ── Qualità dei dati ──────────────────────────────────────────────────────
    ("dq_osr_unknown_resource", "data_quality", "high",
     "OSR with unknown resource",
     "The OSR refers to an EID that is not in the resource list.",
     "Fix the EID on the OSR or add the resource."),
    ("dq_inverted_dates", "data_quality", "high",
     "End date before start date",
     "A contract, opportunity or OSR ends before it starts.",
     "Correct the dates."),
    ("dq_osr_outside_opportunity", "data_quality", "medium",
     "OSR outside opportunity dates",
     "The OSR starts before or ends after its opportunity.",
     "Align the OSR dates with the opportunity."),
    ("dq_opportunity_outside_contract", "data_quality", "medium",
     "Opportunity outside contract dates",
     "The opportunity starts before or ends after its contract.",
     "Align the opportunity dates with the contract."),
    ("dq_resource_no_email", "data_quality", "medium",
     "Resource without email",
     "No email: certifications cannot be linked to the resource.",
     "Fill in the email."),
    ("dq_resource_no_skills", "data_quality", "medium",
     "Resource without skills",
     "No skills recorded: the resource cannot be found by Match AI.",
     "Fill in the skills."),
    ("dq_resource_no_languages", "data_quality", "low",
     "Resource without languages",
     "No languages recorded.",
     "Fill in the languages."),
]

_ORDER = {item[0]: index for index, item in enumerate(CATALOG)}
_SEVERITY = {item[0]: item[2] for item in CATALOG}


def _parse(value):
    if not value:
        return None

    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _is_closed(status):
    return str(status or "").strip().lower() == "closed"


def _full_name(first, last):
    return f"{first or ''} {last or ''}".strip() or None


def build_practice_alerts(expiry_days=30):
    today = date.today()
    limit = today + timedelta(days=expiry_days)

    data = db.sm_get_staffing_management_v2()
    resources = db.sm_get_risorse_v2()

    contracts = data.get("contracts", [])
    opportunities = data.get("opportunities", [])
    osr_rows = data.get("osr", [])

    milestones = db._fetchall("""
        SELECT
            MILESTONEID           AS milestone_id,
            OPPORTUNITYID         AS opportunity_id,
            PONUMBER              AS po_number,
            PROJECTPHASE          AS project_phase,
            MILESTONEDESCRIPTION  AS description,
            BILLABLEAMOUNTEUR     AS amount,
            PLANNEDBILLINGDATE    AS planned_date,
            ACTUALBILLINGDATE     AS actual_date,
            MILESTONESTATUS       AS status
        FROM STAFFMATCH_SM_MILESTONE
    """)

    alerts = []

    def add(code, item_id, title, client=None, owner=None,
            end_date=None, detail=None, severity=None):
        end = _parse(end_date)

        alerts.append({
            "code": code,
            "severity": severity or _SEVERITY[code],
            "item_id": item_id,
            "title": title,
            "client": client,
            "owner": owner,
            "end_date": end.isoformat() if end else None,
            "days_to_end": (end - today).days if end else None,
            "detail": detail
        })

    def add_expiry(prefix, item_id, title, end_date,
                   client=None, owner=None, detail=None):
        end = _parse(end_date)

        if end is None:
            return

        if end < today:
            add(f"{prefix}_expired_open", item_id, title,
                client, owner, end_date, detail)
        elif end <= limit:
            add(f"{prefix}_expiring", item_id, title,
                client, owner, end_date, detail)

    # Mappe di appoggio
    contract_by_id = {c.get("contract_id"): c for c in contracts}
    opportunity_by_id = {
        o.get("opportunity_id"): o for o in opportunities
    }

    active_osr_opportunities = set()

    for osr in osr_rows:
        end = _parse(osr.get("end_date"))

        if end and end >= today:
            active_osr_opportunities.add(osr.get("opportunity_id"))

    milestone_opportunities = {
        m.get("opportunity_id") for m in milestones
    }

    # ── Contratti ─────────────────────────────────────────────────────────────
    for contract in contracts:
        contract_id = contract.get("contract_id")
        title = contract.get("contract_title")
        client = contract.get("client_name")
        manager = _full_name(
            contract.get("manager_nome"),
            contract.get("manager_cognome")
        )
        detail = f"Status: {contract.get('contract_status') or '-'}"

        if _is_closed(contract.get("contract_status")):
            continue

        if contract.get("opportunity_count", 0) == 0:
            add("contract_no_opportunity", contract_id, title, client,
                manager, contract.get("end_date"), detail)

        add_expiry("contract", contract_id, title,
                   contract.get("end_date"), client, manager, detail)

        revenue = contract.get("contract_revenue") or 0
        costs = contract.get("contract_costs") or 0

        if costs > revenue:
            add("contract_negative_margin", contract_id, title, client,
                manager, contract.get("end_date"),
                f"Revenue € {revenue:,.0f} · Costs € {costs:,.0f} · "
                f"Margin € {revenue - costs:,.0f}")

        if manager is None:
            add("contract_no_manager", contract_id, title, client,
                None, contract.get("end_date"), detail)

    # ── Opportunity ───────────────────────────────────────────────────────────
    for opportunity in opportunities:
        if _is_closed(opportunity.get("opportunity_status")):
            continue

        opportunity_id = opportunity.get("opportunity_id")
        title = opportunity.get("opportunity_title")
        client = opportunity.get("client_name")
        status = opportunity.get("opportunity_status")
        is_pipeline = str(status or "").strip().lower() == "pipeline"
        detail = (
            f"Status: {status or '-'} · "
            f"Stage: {opportunity.get('opportunity_stage') or '-'}"
        )
        end_date = opportunity.get("end_date")

        if opportunity.get("contract_missing"):
            add("opportunity_no_contract", opportunity_id, title,
                client, None, end_date, detail)

        if opportunity.get("osr_count", 0) == 0:
            add("opportunity_no_osr", opportunity_id, title, client,
                None, end_date, detail)
        elif opportunity_id not in active_osr_opportunities:
            add("opportunity_no_active_osr", opportunity_id, title,
                client, None, end_date, detail)

        add_expiry("opportunity", opportunity_id, title, end_date,
                   client, None, detail)

        start = _parse(opportunity.get("start_date"))

        if is_pipeline and start and start < today:
            add("opportunity_pipeline_late", opportunity_id, title,
                client, None, end_date,
                f"{detail} · Started on {start.isoformat()}")

        if not is_pipeline and opportunity_id not in milestone_opportunities:
            add("opportunity_no_milestone", opportunity_id, title,
                client, None, end_date, detail)

    # ── OSR ───────────────────────────────────────────────────────────────────
    for osr in osr_rows:
        end = _parse(osr.get("end_date"))

        if end is None or end < today:
            continue

        person = _full_name(
            osr.get("resource_nome"), osr.get("resource_cognome")
        )
        title = f"{person or 'Unknown resource'} · " \
                f"{osr.get('project_role') or '-'}"
        detail = (
            f"Opportunity: {osr.get('opportunity_id') or '-'} · "
            f"Allocation: {osr.get('allocation_pct')}% · "
            f"Chargeability: {osr.get('chargeability_pct')}%"
        )

        if end <= limit:
            add("osr_expiring", osr.get("osr_id"), title,
                osr.get("client_name"), person, osr.get("end_date"),
                detail)

        if (osr.get("chargeability_pct") or 0) < LOW_CHARGEABILITY_PCT:
            add("osr_low_chargeability", osr.get("osr_id"), title,
                osr.get("client_name"), person, osr.get("end_date"),
                detail)

    # ── Risorse ───────────────────────────────────────────────────────────────
    for resource in resources:
        name = _full_name(resource.get("nome"), resource.get("cognome"))
        eid = resource.get("eid")
        base_detail = (
            f"Level: {resource.get('level_name') or '-'}"
            + (" · Intern" if resource.get("is_stagista") else "")
        )

        if not resource.get("has_osr"):
            add("resource_no_osr", eid, name, None, name, None,
                base_detail)
        elif not resource.get("has_valid_osr"):
            add("resource_no_active_osr", eid, name, None, name,
                resource.get("available_from"),
                f"{base_detail} · Last OSR ended on "
                f"{resource.get('available_from') or '-'}")

        allocation = resource.get("active_allocation") or 0

        if allocation > 100:
            add("resource_over_allocated", eid, name, None, name,
                None, f"{base_detail} · Allocated {allocation}%")
        elif 0 < allocation < 100:
            add("resource_under_allocated", eid, name, None, name,
                None,
                f"{base_detail} · Allocated {allocation}% · "
                f"Free {100 - allocation}%")

        for cert in resource.get("certifications", []):
            expiration = _parse(cert.get("expiration_date"))

            if expiration is None:
                continue

            cert_title = f"{name} · {cert.get('nome_cert') or '-'}"

            if expiration < today:
                add("resource_cert_expired", eid, cert_title, None,
                    name, cert.get("expiration_date"),
                    f"Cert ID: {cert.get('cert_id') or '-'}")
            elif expiration <= limit:
                add("resource_cert_expiring", eid, cert_title, None,
                    name, cert.get("expiration_date"),
                    f"Cert ID: {cert.get('cert_id') or '-'}")

        if not (resource.get("email") or "").strip():
            add("dq_resource_no_email", eid, name, None, name, None,
                base_detail)

        if not resource.get("skills"):
            add("dq_resource_no_skills", eid, name, None, name, None,
                base_detail)

        if not resource.get("languages"):
            add("dq_resource_no_languages", eid, name, None, name,
                None, base_detail)

    # ── Fatturazione ──────────────────────────────────────────────────────────
    for milestone in milestones:
        status = str(milestone.get("status") or "").strip().lower()
        billed = (
            milestone.get("actual_date") is not None
            or status == "paid"
        )

        if billed:
            continue

        planned = _parse(milestone.get("planned_date"))
        opportunity = opportunity_by_id.get(
            milestone.get("opportunity_id"), {}
        )
        title = (
            f"{milestone.get('description') or '-'} "
            f"({milestone.get('project_phase') or '-'})"
        )
        client = (
            opportunity.get("client_name")
            or opportunity.get("opportunity_title")
        )
        detail = (
            f"Opportunity: {milestone.get('opportunity_id') or '-'} · "
            f"€ {float(milestone.get('amount') or 0):,.0f} · "
            f"PO: {milestone.get('po_number') or '-'}"
        )

        if status == "overdue" or (planned and planned < today):
            add("milestone_overdue", milestone.get("milestone_id"),
                title, client, None,
                milestone.get("planned_date"), detail)
        elif planned and planned <= limit:
            add("milestone_due_soon", milestone.get("milestone_id"),
                title, client, None,
                milestone.get("planned_date"), detail)

    # ── Qualità dei dati: date ────────────────────────────────────────────────
    def inverted(kind, item_id, title, start, end, client=None):
        start_date, end_date = _parse(start), _parse(end)

        if start_date and end_date and end_date < start_date:
            add("dq_inverted_dates", item_id, f"{kind}: {title}",
                client, None, end,
                f"Start {start_date.isoformat()} · "
                f"End {end_date.isoformat()}")

    for contract in contracts:
        inverted("Contract", contract.get("contract_id"),
                 contract.get("contract_title"),
                 contract.get("start_date"), contract.get("end_date"),
                 contract.get("client_name"))

    for opportunity in opportunities:
        inverted("Opportunity", opportunity.get("opportunity_id"),
                 opportunity.get("opportunity_title"),
                 opportunity.get("start_date"),
                 opportunity.get("end_date"),
                 opportunity.get("client_name"))

    for osr in osr_rows:
        inverted("OSR", osr.get("osr_id"),
                 _full_name(osr.get("resource_nome"),
                            osr.get("resource_cognome")) or "-",
                 osr.get("start_date"), osr.get("end_date"),
                 osr.get("client_name"))

        if osr.get("resource_missing"):
            add("dq_osr_unknown_resource", osr.get("osr_id"),
                f"OSR {osr.get('osr_id')}", osr.get("client_name"),
                None, osr.get("end_date"),
                f"Unknown EID: {osr.get('resource_eid')}")

        opportunity = opportunity_by_id.get(osr.get("opportunity_id"))

        if opportunity:
            osr_start = _parse(osr.get("start_date"))
            osr_end = _parse(osr.get("end_date"))
            opp_start = _parse(opportunity.get("start_date"))
            opp_end = _parse(opportunity.get("end_date"))

            if (
                (osr_start and opp_start and osr_start < opp_start)
                or (osr_end and opp_end and osr_end > opp_end)
            ):
                add("dq_osr_outside_opportunity", osr.get("osr_id"),
                    _full_name(osr.get("resource_nome"),
                               osr.get("resource_cognome"))
                    or f"OSR {osr.get('osr_id')}",
                    osr.get("client_name"), None, osr.get("end_date"),
                    f"OSR {osr.get('start_date')} → "
                    f"{osr.get('end_date')} · Opportunity "
                    f"{opportunity.get('start_date')} → "
                    f"{opportunity.get('end_date')}")

    for opportunity in opportunities:
        contract = contract_by_id.get(opportunity.get("contract_id"))

        if not contract:
            continue

        opp_start = _parse(opportunity.get("start_date"))
        opp_end = _parse(opportunity.get("end_date"))
        contract_start = _parse(contract.get("start_date"))
        contract_end = _parse(contract.get("end_date"))

        if (
            (opp_start and contract_start and opp_start < contract_start)
            or (opp_end and contract_end and opp_end > contract_end)
        ):
            add("dq_opportunity_outside_contract",
                opportunity.get("opportunity_id"),
                opportunity.get("opportunity_title"),
                opportunity.get("client_name"), None,
                opportunity.get("end_date"),
                f"Opportunity {opportunity.get('start_date')} → "
                f"{opportunity.get('end_date')} · Contract "
                f"{contract.get('start_date')} → "
                f"{contract.get('end_date')}")

    alerts.sort(key=lambda a: (
        _ORDER[a["code"]],
        a["days_to_end"] if a["days_to_end"] is not None else 99999
    ))

    texts = {"days": expiry_days, "charge": LOW_CHARGEABILITY_PCT}

    return {
        "today": today.isoformat(),
        "expiry_days": expiry_days,
        "low_chargeability_pct": LOW_CHARGEABILITY_PCT,
        "catalog": [
            {
                "code": code,
                "area": area,
                "severity": severity,
                "label": label,
                "description": description.format(**texts),
                "action": action
            }
            for code, area, severity, label, description, action
            in CATALOG
        ],
        "alerts": alerts
    }
