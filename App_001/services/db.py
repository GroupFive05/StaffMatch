import os
import json
from hdbcli import dbapi

_conn = None

def _get_conn():
    global _conn
    try:
        if _conn is not None:
            _conn.cursor().execute("SELECT 1 FROM DUMMY")
            return _conn
    except:
        _conn = None
    _conn = dbapi.connect(
        address=os.environ.get("HANA_ADDRESS", "268718a1-2b08-4eb6-99ec-87a77e84bab0.hna2.prod-eu10.hanacloud.ondemand.com"),
        port=int(os.environ.get("HANA_PORT", "443")),
        user=os.environ.get("HANA_USER", "43986AB4EB174D8AAB87650958CCA6AD_31OU7WNFBO7Y4JDWIWL6COUSQ_RT"),
        password=os.environ.get("HANA_PASSWORD", "Mq9SnAW4NkeTlQdMql_fxBSZAqijMBIx5MMJHx0r-7O47-OYE.7O.dTJAmE2RTOMSPqU0CQvdlof-WmDKkSX7jO0Z4Mnt_ZM9UIrd-A2gUfgVGo3rvOB9W1w7ku3hgMK"),
        encrypt=True,
        sslValidateCertificate=True,
        currentSchema=os.environ.get("HANA_SCHEMA", "43986AB4EB174D8AAB87650958CCA6AD")
    )
    return _conn

def _fetchall(query, params=()):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    cols = [d[0].lower() for d in cur.description]
    rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    return rows

def _execute(query, params=()):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()

def get_skills():
    return _fetchall("SELECT ID as id, NOME as nome, CATEGORIA as categoria, DESCRIZIONE as descrizione FROM STAFFMATCH_SKILL")

def save_skills(data):
    _execute("DELETE FROM STAFFMATCH_SKILL")
    for s in data:
        _execute("INSERT INTO STAFFMATCH_SKILL (ID, NOME, CATEGORIA, DESCRIZIONE) VALUES (?,?,?,?)",
                 (s.get("id"), s.get("nome"), s.get("categoria",""), s.get("descrizione","")))

def get_roles():
    return _fetchall("SELECT ID as id, NOME as nome, SENIORITY as seniority, DESCRIZIONE as descrizione, COSTOORARIO as costo_orario FROM STAFFMATCH_RUOLO")

def save_roles(data):
    _execute("DELETE FROM STAFFMATCH_RUOLO")
    for r in data:
        _execute("INSERT INTO STAFFMATCH_RUOLO (ID, NOME, SENIORITY, DESCRIZIONE, COSTOORARIO) VALUES (?,?,?,?,?)",
                 (r.get("id"), r.get("nome"), r.get("seniority",""), r.get("descrizione",""), r.get("costo_orario",0)))

def get_role_groups():
    rows = _fetchall("SELECT ID as id, NOME as nome, DESCRIZIONE as descrizione, RUOLIIDS as ruoli_ids FROM STAFFMATCH_GRUPPORUOLO")
    for r in rows:
        try:
            r["ruoli_ids"] = json.loads(r.get("ruoli_ids") or "[]")
        except:
            r["ruoli_ids"] = []
    return rows

def save_role_groups(data):
    _execute("DELETE FROM STAFFMATCH_GRUPPORUOLO")
    for g in data:
        _execute("INSERT INTO STAFFMATCH_GRUPPORUOLO (ID, NOME, DESCRIZIONE, RUOLIIDS) VALUES (?,?,?,?)",
                 (g.get("id"), g.get("nome"), g.get("descrizione",""), json.dumps(g.get("ruoli_ids",[]))))

def get_resources():
    risorse = _fetchall("SELECT ID as id, NOME as nome, COGNOME as cognome, EMAIL as email, DATANASCITA as data_nascita, RUOLOID as ruolo_id, COSTOORARIO as costo_orario, LINGUE as lingue, ISACTIVE as is_active, PASSWORDHASH as password_hash, GRUPPORUOLOIDS as gruppo_ruolo_ids, DISPONIBILITA as disponibilita, TERMINEPROGETTO as termine_progetto, OFFSHORE as offshore, STAGISTA as stagista, MOVIMENTOINCORSO as movimento_in_corso FROM STAFFMATCH_RISORSA")
    for r in risorse:
        try:
            r["lingue"] = json.loads(r.get("lingue") or "[]")
        except:
            r["lingue"] = []
        try:
            r["gruppo_ruolo_ids"] = json.loads(r.get("gruppo_ruolo_ids") or "[]")
        except:
            r["gruppo_ruolo_ids"] = []
        skills = _fetchall("SELECT SKILLID as skill_id, LIVELLO as livello FROM STAFFMATCH_RISORSASKILL WHERE RISORSAID = ?", (r["id"],))
        r["skill_ids"] = skills
    return risorse

def save_resources(data):
    _execute("DELETE FROM STAFFMATCH_RISORSASKILL")
    _execute("DELETE FROM STAFFMATCH_RISORSA")
    for r in data:
        _execute("""INSERT INTO STAFFMATCH_RISORSA
                 (ID, NOME, COGNOME, EMAIL, DATANASCITA, RUOLOID, COSTOORARIO,
                  LINGUE, ISACTIVE, PASSWORDHASH, GRUPPORUOLOIDS,
                  DISPONIBILITA, TERMINEPROGETTO, OFFSHORE, STAGISTA, MOVIMENTOINCORSO)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                 (r.get("id"), r.get("nome"), r.get("cognome"), r.get("email"),
                  r.get("data_nascita"), r.get("ruolo_id"), r.get("costo_orario",0),
                  json.dumps(r.get("lingue",[])), r.get("is_active",True),
                  r.get("password_hash",""), json.dumps(r.get("gruppo_ruolo_ids",[])),
                  r.get("disponibilita",100), r.get("termine_progetto"),
                  r.get("offshore",False), r.get("stagista",False),
                  r.get("movimento_in_corso",False)))
        for sk in r.get("skill_ids", []):
            _execute("INSERT INTO STAFFMATCH_RISORSASKILL (RISORSAID, SKILLID, LIVELLO) VALUES (?,?,?)",
                     (r.get("id"), sk.get("skill_id"), sk.get("livello",1)))

def get_opportunities():
    opps = _fetchall("SELECT ID as id, TITOLO as titolo, CLIENTE as cliente, REFERENTENOME as referente_nome, REFERENTECOGNOME as referente_cognome, MANAGERID as manager_id, DATAINIZIO as data_inizio, DATAFINEPREVISTA as data_fine_prevista, STATO as stato, DESCRIZIONE as descrizione, PRIORITA as priorita FROM STAFFMATCH_OPPORTUNITY")
    for o in opps:
        o["referente_it_cliente"] = {"nome": o.pop("referente_nome",""), "cognome": o.pop("referente_cognome","")}
        o["skill_richieste"] = _fetchall("SELECT SKILLID as skill_id, LIVELLOMINIMO as livello_minimo FROM STAFFMATCH_OPPORTUNITYSKILL WHERE OPPORTUNITYID = ?", (o["id"],))
        o["slot_risorse"] = _fetchall("SELECT SLOTINDEX as slot_index, MANSIONEID as mansione_id, PERCENTUALEALLOCAZIONE as percentuale_allocazione FROM STAFFMATCH_OPPORTUNITYSLOT WHERE OPPORTUNITYID = ? ORDER BY SLOTINDEX", (o["id"],))
    return opps

def save_opportunities(data):
    _execute("DELETE FROM STAFFMATCH_OPPORTUNITYSKILL")
    _execute("DELETE FROM STAFFMATCH_OPPORTUNITYSLOT")
    _execute("DELETE FROM STAFFMATCH_OPPORTUNITY")
    for o in data:
        ref = o.get("referente_it_cliente", {})
        _execute("""INSERT INTO STAFFMATCH_OPPORTUNITY
                 (ID, TITOLO, CLIENTE, REFERENTENOME, REFERENTECOGNOME,
                  MANAGERID, DATAINIZIO, DATAFINEPREVISTA, STATO, DESCRIZIONE, PRIORITA)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                 (o.get("id"), o.get("titolo"), o.get("cliente"),
                  ref.get("nome",""), ref.get("cognome",""),
                  o.get("manager_id",""), o.get("data_inizio"),
                  o.get("data_fine_prevista"), o.get("stato","New"),
                  o.get("descrizione",""), o.get("priorita",0)))
        for sk in o.get("skill_richieste", []):
            _execute("INSERT INTO STAFFMATCH_OPPORTUNITYSKILL (OPPORTUNITYID, SKILLID, LIVELLOMINIMO) VALUES (?,?,?)",
                     (o.get("id"), sk.get("skill_id"), sk.get("livello_minimo",1)))
        for i, slot in enumerate(o.get("slot_risorse", [])):
            _execute("INSERT INTO STAFFMATCH_OPPORTUNITYSLOT (OPPORTUNITYID, SLOTINDEX, MANSIONEID, PERCENTUALEALLOCAZIONE) VALUES (?,?,?,?)",
                     (o.get("id"), i, slot.get("mansione_id",""), slot.get("percentuale_allocazione",100)))

def get_projects():
    projs = _fetchall("SELECT ID as id, NOME as nome, CLIENTE as cliente, REFERENTENOME as referente_nome, REFERENTECOGNOME as referente_cognome, MANAGERID as manager_id, SKILLPRINCIPALEID as skill_principale_id, SKILLSECONDARIE as skill_secondarie_ids, DATAINIZIO as data_inizio, DATAFINEPREVISTA as data_fine_prevista, STATO as stato, DESCRIZIONE as descrizione FROM STAFFMATCH_PROGETTO")
    for p in projs:
        p["referente_it_cliente"] = {"nome": p.pop("referente_nome",""), "cognome": p.pop("referente_cognome","")}
        try:
            p["skill_secondarie_ids"] = json.loads(p.get("skill_secondarie_ids") or "[]")
        except:
            p["skill_secondarie_ids"] = []
    return projs

def save_projects(data):
    _execute("DELETE FROM STAFFMATCH_PROGETTO")
    for p in data:
        ref = p.get("referente_it_cliente", {})
        _execute("""INSERT INTO STAFFMATCH_PROGETTO
                 (ID, NOME, CLIENTE, REFERENTENOME, REFERENTECOGNOME,
                  MANAGERID, SKILLPRINCIPALEID, SKILLSECONDARIE,
                  DATAINIZIO, DATAFINEPREVISTA, STATO, DESCRIZIONE)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                 (p.get("id"), p.get("nome"), p.get("cliente"),
                  ref.get("nome",""), ref.get("cognome",""),
                  p.get("manager_id",""), p.get("skill_principale_id",""),
                  json.dumps(p.get("skill_secondarie_ids",[])),
                  p.get("data_inizio"), p.get("data_fine_prevista"),
                  p.get("stato","Active"), p.get("descrizione","")))

def get_allocations():
    return _fetchall("SELECT ID as id, RISORSAID as risorsa_id, PROGETTOID as progetto_id, PERCENTUALE as percentuale, DATAINIZIO as data_inizio, DATAFINE as data_fine, RUOLONELPROGETTO as ruolo_nel_progetto FROM STAFFMATCH_ALLOCAZIONE")

def save_allocations(data):
    _execute("DELETE FROM STAFFMATCH_ALLOCAZIONE")
    for a in data:
        _execute("INSERT INTO STAFFMATCH_ALLOCAZIONE (ID, RISORSAID, PROGETTOID, PERCENTUALE, DATAINIZIO, DATAFINE, RUOLONELPROGETTO) VALUES (?,?,?,?,?,?,?)",
                 (a.get("id"), a.get("risorsa_id"), a.get("progetto_id"),
                  a.get("percentuale",100), a.get("data_inizio"),
                  a.get("data_fine"), a.get("ruolo_nel_progetto","")))

def get_match_results():
    return _fetchall("SELECT ID as id, OPPORTUNITYID as opportunity_id, SLOTINDEX as slot_index, RISORSAID as risorsa_id, SCORE as score, MOTIVAZIONE as motivazione, STATO as stato FROM STAFFMATCH_MATCHRESULT")

def save_match_results(data):
    _execute("DELETE FROM STAFFMATCH_MATCHRESULT")
    for m in data:
        _execute("INSERT INTO STAFFMATCH_MATCHRESULT (ID, OPPORTUNITYID, SLOTINDEX, RISORSAID, SCORE, MOTIVAZIONE, STATO) VALUES (?,?,?,?,?,?,?)",
                 (m.get("id"), m.get("opportunity_id"), m.get("slot_index",0),
                  m.get("risorsa_id"), m.get("score",0),
                  m.get("motivazione",""), m.get("stato","Proposed")))

def get_promotion_requests():
    rows = _fetchall("SELECT ID as id, OPPORTUNITYID as opportunity_id, OPPORTUNITYTITOLO as opportunity_titolo, OPPORTUNITYCLIENTE as opportunity_cliente, REQUESTEDBYID as requested_by_id, REQUESTEDBYNOME as requested_by_nome, REQUESTEDAT as requested_at, STATO as stato, NOTEMANAGER as note_manager, NOTEEXECUTIVE as note_executive, REVIEWEDBYID as reviewed_by_id, REVIEWEDAT as reviewed_at, RISOREPERSLOT as risorse_per_slot FROM STAFFMATCH_PROMOTIONREQUEST")
    for r in rows:
        try:
            r["risorse_per_slot"] = json.loads(r.get("risorse_per_slot") or "[]")
        except:
            r["risorse_per_slot"] = []
    return rows

def save_promotion_requests(data):
    _execute("DELETE FROM STAFFMATCH_PROMOTIONREQUEST")
    for r in data:
        _execute("""INSERT INTO STAFFMATCH_PROMOTIONREQUEST
                 (ID, OPPORTUNITYID, OPPORTUNITYTITOLO, OPPORTUNITYCLIENTE,
                  REQUESTEDBYID, REQUESTEDBYNOME, REQUESTEDAT, STATO,
                  NOTEMANAGER, NOTEEXECUTIVE, REVIEWEDBYID, REVIEWEDAT, RISOREPERSLOT)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                 (r.get("id"), r.get("opportunity_id"), r.get("opportunity_titolo",""),
                  r.get("opportunity_cliente",""), r.get("requested_by_id",""),
                  r.get("requested_by_nome",""), r.get("requested_at",""),
                  r.get("stato","Pending"), r.get("note_manager",""),
                  r.get("note_executive"), r.get("reviewed_by_id"),
                  r.get("reviewed_at"), json.dumps(r.get("risorse_per_slot",[]))))

def get_project_change_requests():
    rows = _fetchall("SELECT ID as id, PROJECTID as project_id, PROJECTNOME as project_nome, PROJECTCLIENTE as project_cliente, REQUESTEDBYID as requested_by_id, REQUESTEDBYNOME as requested_by_nome, REQUESTEDAT as requested_at, STATO as stato, CHANGETYPE as change_type, PAYLOAD as payload, NOTEMANAGER as note_manager, NOTEEXECUTIVE as note_executive, REVIEWEDBYID as reviewed_by_id, REVIEWEDAT as reviewed_at FROM STAFFMATCH_PROJECTCHANGEREQUEST")
    for r in rows:
        try:
            r["payload"] = json.loads(r.get("payload") or "{}")
        except:
            r["payload"] = {}
    return rows

def save_project_change_requests(data):
    _execute("DELETE FROM STAFFMATCH_PROJECTCHANGEREQUEST")
    for r in data:
        _execute("""INSERT INTO STAFFMATCH_PROJECTCHANGEREQUEST
                 (ID, PROJECTID, PROJECTNOME, PROJECTCLIENTE,
                  REQUESTEDBYID, REQUESTEDBYNOME, REQUESTEDAT, STATO,
                  CHANGETYPE, PAYLOAD, NOTEMANAGER, NOTEEXECUTIVE,
                  REVIEWEDBYID, REVIEWEDAT)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                 (r.get("id"), r.get("project_id"), r.get("project_nome",""),
                  r.get("project_cliente",""), r.get("requested_by_id",""),
                  r.get("requested_by_nome",""), r.get("requested_at",""),
                  r.get("stato","Pending"), r.get("change_type",""),
                  json.dumps(r.get("payload",{})), r.get("note_manager",""),
                  r.get("note_executive"), r.get("reviewed_by_id"),
                  r.get("reviewed_at")))

def disponibilita_risorsa(risorsa_id: str) -> int:
    allocazioni = [a for a in get_allocations() if a.get("risorsa_id") == risorsa_id]
    totale = sum(a.get("percentuale", 0) for a in allocazioni)
    return max(0, 100 - totale)

def get_risorse_acn():
    return _fetchall(
        "SELECT ID as id, LEVEL as level, ANNIESPERIENZA as anni_esperienza, "
        "DISPONIBILITA as disponibilita, AVAILABLEFROM as available_from, "
        "ISSTAGISTA as is_stagista FROM STAFFMATCH_RISORSAACN"
    )

def get_cert_catalog():
    return _fetchall(
        "SELECT CERTID as cert_id, NOMECERT as nome_cert, VENDOR as vendor, "
        "CATEGORIA as categoria FROM STAFFMATCH_CERTCATALOG"
    )

def get_contracts():
    return _fetchall(
        "SELECT CONTRACTID as contract_id, CONTRACTTITLE as contract_title, "
        "CLIENTNAME as client_name, INDUSTRYSECTOR as industry_sector, "
        "COUNTRY as country, CONTRACTMANAGER as contract_manager, CAL as cal, "
        "SERVICEGROUP as service_group, PRACTICELEAD as practice_lead, "
        "DATAINIZIO as data_inizio, DATAFINE as data_fine, "
        "CONTRACTREVENUE as contract_revenue, COSTI as costi, "
        "CONTRACTSTATUS as contract_status, ISCROSSPRACTICE as is_cross_practice, "
        "DAPRACTICEPCT as da_practice_pct FROM STAFFMATCH_CONTRACT"
    )

def get_milestones():
    return _fetchall(
        "SELECT MILESTONEID as milestone_id, OPPORTUNITYID as opportunity_id, "
        "PONUMBER as po_number, PROJECTPHASE as project_phase, "
        "MILESTONEDESCRIPTION as milestone_description, "
        "BILLABLEAMOUNTEUR as billable_amount_eur, "
        "PLANNEDBILLINGDATE as planned_billing_date, "
        "ACTUALBILLINGDATE as actual_billing_date, "
        "MILESTONESTATUS as milestone_status, INVOICENUMBER as invoice_number "
        "FROM STAFFMATCH_MILESTONE"
    )

def get_osr():
    return _fetchall(
        "SELECT OSRID as osr_id, ID as id, OPPORTUNITYID as opportunity_id, "
        "RUOLOINPROGETTO as ruolo_in_progetto, PERCALLOCAZIONE as perc_allocazione, "
        "CHARGEABILITYPCT as chargeability_pct, DATAINIZIO as data_inizio, "
        "DATAFINE as data_fine, STATO as stato FROM STAFFMATCH_OSR"
    )

# ══════════════════════════════════════════════════════════
# SM_* — nuovo modello dati (Valerio / GroupFive05) — tabelle con dati reali
# ══════════════════════════════════════════════════════════

def sm_get_risorse():
    risorse = _fetchall("""
        SELECT EID as eid, NOME as nome, COGNOME as cognome, LEVEL as level,
               LEVELNAME as level_name, ANNIESPERIENZA as anni_esperienza,
               DISPONIBILITA as disponibilita, AVAILABLEFROM as available_from,
               ISSTAGISTA as is_stagista
        FROM STAFFMATCH_SM_RISORSA
    """)
    for r in risorse:
        skills = _fetchall(
            "SELECT SKILLNAME as skill_name FROM STAFFMATCH_SM_RISORSASKILL WHERE EID = ?",
            (r["eid"],)
        )
        r["skills"] = [s["skill_name"] for s in skills]
        certs = _fetchall(
            "SELECT CERTID as cert_id FROM STAFFMATCH_SM_RISORSACERT WHERE EID = ?",
            (r["eid"],)
        )
        r["cert_ids"] = [c["cert_id"] for c in certs]
        langs = _fetchall(
            "SELECT LANGUAGECODE as language_code FROM STAFFMATCH_SM_RISORSALANGUAGE WHERE EID = ?",
            (r["eid"],)
        )
        r["lingue"] = [l["language_code"] for l in langs]
    return risorse


def sm_get_disponibilita_calcolata(eid):
    rows = _fetchall(
        "SELECT PERCALLOCAZIONE as perc FROM STAFFMATCH_SM_OSR WHERE EID = ? AND STATO = 'Active'",
        (eid,)
    )
    allocato = sum(r["perc"] for r in rows)
    return max(0, 100 - allocato)


def sm_get_opportunities():
    opps = _fetchall("""
        SELECT OPPORTUNITYID as opportunity_id, OPPORTUNITYTITLE as titolo,
               CONTRACTID as contract_id, OPPORTUNITYSTAGE as stage,
               MAINTECHCLUSTER as main_tech_cluster, FUNCTIONALAREA as functional_area,
               DATAINIZIO as data_inizio, DATAFINE as data_fine,
               OPPORTUNITYVALUE as valore, OPPORTUNITYSTATUS as stato
        FROM STAFFMATCH_SM_OPPORTUNITY
    """)
    for o in opps:
        o["cliente"] = None
        if o["contract_id"]:
            contratto = _fetchall(
                "SELECT CLIENTNAME as client_name FROM STAFFMATCH_SM_CONTRACT WHERE CONTRACTID = ?",
                (o["contract_id"],)
            )
            if contratto:
                o["cliente"] = contratto[0]["client_name"]
    return opps


def _skill_matches_cluster(skill_name, tech_cluster):
    skill_norm = (skill_name or "").lower().strip()
    cluster_norm = (tech_cluster or "").lower().strip()
    return skill_norm in cluster_norm or cluster_norm in skill_norm


def sm_match_score(risorsa, opportunity):
    skill_hit = any(
        _skill_matches_cluster(s, opportunity["main_tech_cluster"])
        for s in risorsa["skills"]
    )
    skill_score = 60 if skill_hit else 0
    disp = sm_get_disponibilita_calcolata(risorsa["eid"])
    disp_score = min(40, int(disp * 0.4))
    return {
        "eid": risorsa["eid"],
        "nome": f"{risorsa['nome']} {risorsa['cognome']}",
        "score": skill_score + disp_score,
        "skill_match": skill_hit,
        "disponibilita": disp,
        "motivazione": (
            f"{'Competenza' if skill_hit else 'Nessuna competenza diretta'} su "
            f"{opportunity['main_tech_cluster']}, disponibilità {disp}%"
        )
    }
def sm_get_risorse_v2():
    """
    Risorse V2 con:
    - anagrafica
    - skill
    - lingue
    - certificazioni
    - disponibilità calcolata dalle OSR
    - manager di riferimento
    """

    from datetime import date, datetime

    def to_date(value):
        if value is None:
            return None

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        value = str(value)[:10]

        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None

    today = date.today()

    # ── Anagrafica risorse ────────────────────────────────────────────────────
    resources = _fetchall("""
        SELECT
            EID            AS eid,
            NOME           AS nome,
            COGNOME        AS cognome,
            EMAIL          AS email,
            LEVEL          AS level,
            LEVELNAME      AS level_name,
            ANNIESPERIENZA AS anni_esperienza,
            ISSTAGISTA     AS is_stagista
        FROM STAFFMATCH_SM_RISORSA
        ORDER BY COGNOME, NOME
    """)

    # ── Skill ─────────────────────────────────────────────────────────────────
    skill_rows = _fetchall("""
        SELECT
            EID       AS eid,
            SKILLNAME AS skill_name
        FROM STAFFMATCH_SM_RISORSASKILL
        ORDER BY EID, SKILLNAME
    """)

    skills_by_eid = {}

    for row in skill_rows:
        skills_by_eid.setdefault(
            row["eid"],
            []
        ).append({
            "skill_name": row.get("skill_name")
        })

    # ── Lingue ────────────────────────────────────────────────────────────────
    language_rows = _fetchall("""
        SELECT
            EID          AS eid,
            LANGUAGECODE AS language_code
        FROM STAFFMATCH_SM_RISORSALANGUAGE
        ORDER BY EID, LANGUAGECODE
    """)

    languages_by_eid = {}

    for row in language_rows:
        languages_by_eid.setdefault(
            row["eid"],
            []
        ).append({
            "language_code": row.get("language_code")
        })

    # ── Certificazioni: join tramite email ────────────────────────────────────
    certification_rows = _fetchall("""
        SELECT
            EMAIL          AS email,
            CERTID         AS cert_id,
            NOMECERT       AS nome_cert,
            CITY           AS city,
            LEVEL          AS level,
            LEVELNAME      AS level_name,
            EXPIRATIONDATE AS expiration_date
        FROM STAFFMATCH_SM_RISORSACERT
        ORDER BY EMAIL, EXPIRATIONDATE, NOMECERT
    """)

    certifications_by_email = {}

    for row in certification_rows:
        email = (row.get("email") or "").strip().lower()

        expiration_date = to_date(
            row.get("expiration_date")
        )

        certifications_by_email.setdefault(
            email,
            []
        ).append({
            "cert_id": row.get("cert_id"),
            "nome_cert": row.get("nome_cert"),
            "city": row.get("city"),
            "level": row.get("level"),
            "level_name": row.get("level_name"),
            "expiration_date": (
                expiration_date.isoformat()
                if expiration_date
                else None
            )
        })

    # ── OSR + risalita al manager ─────────────────────────────────────────────
    osr_rows = _fetchall("""
        SELECT
            o.EID              AS eid,
            o.OSRID            AS osr_id,
            o.OPPORTUNITYID    AS opportunity_id,
            o.PERCALLOCAZIONE  AS perc_allocazione,
            o.DATAINIZIO       AS data_inizio,
            o.DATAFINE         AS data_fine,
            c.EID              AS manager_eid,
            m.NOME             AS manager_nome,
            m.COGNOME          AS manager_cognome,
            m.EMAIL            AS manager_email
        FROM STAFFMATCH_SM_OSR o

        LEFT JOIN STAFFMATCH_SM_OPPORTUNITY op
            ON op.OPPORTUNITYID = o.OPPORTUNITYID

        LEFT JOIN STAFFMATCH_SM_CONTRACT c
            ON c.CONTRACTID = op.CONTRACTID

        LEFT JOIN STAFFMATCH_SM_RISORSA m
            ON m.EID = c.EID

        ORDER BY o.EID, o.DATAFINE
    """)

    osr_by_eid = {}

    for row in osr_rows:
        row["data_inizio_date"] = to_date(
            row.get("data_inizio")
        )

        row["data_fine_date"] = to_date(
            row.get("data_fine")
        )

        osr_by_eid.setdefault(
            row["eid"],
            []
        ).append(row)

    # ── Composizione risultato ────────────────────────────────────────────────
    for resource in resources:
        eid = resource.get("eid")

        email = (
            resource.get("email")
            or ""
        ).strip().lower()

        resource["skills"] = skills_by_eid.get(
            eid,
            []
        )

        resource["languages"] = languages_by_eid.get(
            eid,
            []
        )

        resource["certifications"] = certifications_by_email.get(
            email,
            []
        )

        resource_osr = osr_by_eid.get(
            eid,
            []
        )

        # OSR ancora valide in base alla data fine
        valid_osr = [
            osr for osr in resource_osr
            if osr.get("data_fine_date")
            and osr["data_fine_date"] >= today
        ]

        active_allocation = sum(
            int(osr.get("perc_allocazione") or 0)
            for osr in valid_osr
        )

        availability = max(
            0,
            100 - active_allocation
        )

        # Stato semaforico
        if active_allocation == 0:
            availability_status = "green"
        elif active_allocation < 100:
            availability_status = "orange"
        else:
            availability_status = "red"

        # Prima data futura in cui termina una OSR valida
        if valid_osr:
            next_available_date = min(
                osr["data_fine_date"]
                for osr in valid_osr
            )
        else:
            # Se tutte le OSR sono terminate,
            # mostriamo la data fine più recente
            expired_dates = [
                osr.get("data_fine_date")
                for osr in resource_osr
                if osr.get("data_fine_date")
            ]

            next_available_date = (
                max(expired_dates)
                if expired_dates
                else None
            )
        # Manager associati esclusivamente alle OSR ancora valide
        managers = {}

        for osr in valid_osr:
            manager_eid = osr.get("manager_eid")

            if manager_eid is not None:
                managers[manager_eid] = {
                    "eid": manager_eid,
                    "nome": osr.get("manager_nome"),
                    "cognome": osr.get("manager_cognome"),
                    "email": osr.get("manager_email")
                }

        resource["active_allocation"] = active_allocation
        resource["disponibilita"] = availability
        resource["availability_status"] = availability_status
        resource["has_valid_osr"] = bool(valid_osr)
        resource["has_osr"] = bool(resource_osr)

        resource["available_from"] = (
            next_available_date.isoformat()
            if next_available_date
            else None
        )

        resource["managers"] = list(
            managers.values()
        )

        resource["is_stagista"] = bool(
            resource.get("is_stagista")
        )

    return resources
def sm_get_resource_form_catalogs():

    levels = _fetchall("""
        SELECT DISTINCT
            LEVEL AS level,
            LEVELNAME AS level_name
        FROM STAFFMATCH_SM_RISORSA
        WHERE LEVEL IS NOT NULL
        ORDER BY LEVEL
    """)

    skills = _fetchall("""
        SELECT DISTINCT
            SKILLNAME AS skill_name
        FROM STAFFMATCH_SM_RISORSASKILL
        WHERE SKILLNAME IS NOT NULL
        ORDER BY SKILLNAME
    """)

    languages = _fetchall("""
        SELECT DISTINCT
            LANGUAGECODE AS language_code
        FROM STAFFMATCH_SM_RISORSALANGUAGE
        WHERE LANGUAGECODE IS NOT NULL
        ORDER BY LANGUAGECODE
    """)

    certifications = _fetchall("""
        SELECT
            CERTID AS cert_id,
            NOMECERT AS nome_cert,
            VENDOR AS vendor,
            CATEGORIA AS categoria
        FROM STAFFMATCH_SM_CERTCATALOG
        ORDER BY NOMECERT
    """)

    return {
        "levels": levels,
        "skills": skills,
        "languages": languages,
        "certifications": certifications
    }
def sm_create_resource_v2(data):
    """
    Crea una risorsa V2 e i relativi dati collegati
    in un'unica transazione HANA.
    """

    conn = _get_conn()
    cur = conn.cursor()

    try:
        eid = int(data["eid"])
        nome = str(data["nome"]).strip()
        cognome = str(data["cognome"]).strip()
        email = str(data["email"]).strip().lower()
        level = int(data["level"])
        anni_esperienza = int(data.get("anni_esperienza") or 0)
        is_stagista = bool(data.get("is_stagista", False))

        skills = data.get("skills") or []
        languages = data.get("languages") or []
        certifications = data.get("certifications") or []

        if not nome:
            raise ValueError("Il nome è obbligatorio.")

        if not cognome:
            raise ValueError("Il cognome è obbligatorio.")

        if not email:
            raise ValueError("L'email è obbligatoria.")

        # ── Controllo EID ──────────────────────────────────────────────────────
        cur.execute(
            """
            SELECT COUNT(*)
            FROM STAFFMATCH_SM_RISORSA
            WHERE EID = ?
            """,
            (eid,)
        )

        if cur.fetchone()[0] > 0:
            raise ValueError(
                f"Esiste già una risorsa con EID {eid}."
            )

        # ── Controllo email ────────────────────────────────────────────────────
        cur.execute(
            """
            SELECT COUNT(*)
            FROM STAFFMATCH_SM_RISORSA
            WHERE LOWER(EMAIL) = LOWER(?)
            """,
            (email,)
        )

        if cur.fetchone()[0] > 0:
            raise ValueError(
                f"Esiste già una risorsa con email {email}."
            )

        # ── Recupero level name dal DB ─────────────────────────────────────────
        cur.execute(
            """
            SELECT DISTINCT LEVELNAME
            FROM STAFFMATCH_SM_RISORSA
            WHERE LEVEL = ?
            """,
            (level,)
        )

        level_row = cur.fetchone()

        if level_row is None:
            raise ValueError(
                f"Level {level} non presente nei valori ammessi."
            )

        level_name = level_row[0]

        # ── Validazione skill ──────────────────────────────────────────────────
        valid_skills = set()

        cur.execute("""
            SELECT DISTINCT SKILLNAME
            FROM STAFFMATCH_SM_RISORSASKILL
            WHERE SKILLNAME IS NOT NULL
        """)

        for row in cur.fetchall():
            valid_skills.add(row[0])

        invalid_skills = [
            skill
            for skill in skills
            if skill not in valid_skills
        ]

        if invalid_skills:
            raise ValueError(
                "Skill non valide: "
                + ", ".join(invalid_skills)
            )

        # ── Validazione lingue ─────────────────────────────────────────────────
        valid_languages = set()

        cur.execute("""
            SELECT DISTINCT LANGUAGECODE
            FROM STAFFMATCH_SM_RISORSALANGUAGE
            WHERE LANGUAGECODE IS NOT NULL
        """)

        for row in cur.fetchall():
            valid_languages.add(row[0])

        invalid_languages = [
            language
            for language in languages
            if language not in valid_languages
        ]

        if invalid_languages:
            raise ValueError(
                "Lingue non valide: "
                + ", ".join(invalid_languages)
            )

        # ── Catalogo certificazioni ────────────────────────────────────────────
        cur.execute("""
            SELECT
                CERTID,
                NOMECERT
            FROM STAFFMATCH_SM_CERTCATALOG
        """)

        certification_catalog = {
            row[0]: row[1]
            for row in cur.fetchall()
        }

        for certification in certifications:
            cert_id = certification.get("cert_id")

            if cert_id not in certification_catalog:
                raise ValueError(
                    f"Certificazione non valida: {cert_id}."
                )

        # ── Inserimento risorsa ────────────────────────────────────────────────
        cur.execute(
            """
            INSERT INTO STAFFMATCH_SM_RISORSA (
                EID,
                NOME,
                COGNOME,
                EMAIL,
                LEVEL,
                LEVELNAME,
                ANNIESPERIENZA,
                DISPONIBILITA,
                AVAILABLEFROM,
                ISSTAGISTA
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                eid,
                nome,
                cognome,
                email,
                level,
                level_name,
                anni_esperienza,
                100,
                None,
                is_stagista
            )
        )

        # ── Inserimento skill ──────────────────────────────────────────────────
        for skill in sorted(set(skills)):
            cur.execute(
                """
                INSERT INTO STAFFMATCH_SM_RISORSASKILL (
                    EID,
               SKILLNAME
                )
                VALUES (?, ?)
                """,
                (
                    eid,
                    skill
                )
            )

        # ── Inserimento lingue ────────────────────────────────────────────────
        for language in sorted(set(languages)):
            cur.execute(
                """
                INSERT INTO STAFFMATCH_SM_RISORSALANGUAGE (
                    EID,
                    LANGUAGECODE
                )
                VALUES (?, ?)
                """,
                (
                    eid,
                    language
                )
            )

        # ── Inserimento certificazioni ─────────────────────────────────────────
        inserted_certifications = set()

        for certification in certifications:
            cert_id = certification["cert_id"]

            if cert_id in inserted_certifications:
                raise ValueError(
                    f"Certificazione duplicata: {cert_id}."
                )

            inserted_certifications.add(cert_id)

            expiration_date = certification.get(
                "expiration_date"
            )

            city = (
                certification.get("city")
                or ""
            ).strip()

            cur.execute(
                """
                INSERT INTO STAFFMATCH_SM_RISORSACERT (
                    EMAIL,
                    CERTID,
                    NOMECERT,
                    CITY,
                    LEVEL,
                    LEVELNAME,
                    EXPIRATIONDATE
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    email,
                    cert_id,
                    certification_catalog[cert_id],
                    city,
                    level,
                    level_name,
                    expiration_date
                )
            )

        # Un solo commit per tutta l'operazione
        conn.commit()

        return {
            "success": True,
            "message": "Risorsa creata correttamente.",
            "eid": eid,
            "email": email,
            "skills_inserted": len(set(skills)),
            "languages_inserted": len(set(languages)),
            "certifications_inserted": len(
                inserted_certifications
            )
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()