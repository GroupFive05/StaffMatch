import os
import json
from hdbcli import dbapi

def _get_conn():
    return dbapi.connect(
        address=os.environ.get("HANA_ADDRESS", "268718a1-2b08-4eb6-99ec-87a77e84bab0.hna2.prod-eu10.hanacloud.ondemand.com"),
        port=int(os.environ.get("HANA_PORT", "443")),
        user=os.environ.get("HANA_USER", "43986AB4EB174D8AAB87650958CCA6AD_31OU7WNFBO7Y4JDWIWL6COUSQ_RT"),
        password=os.environ.get("HANA_PASSWORD", "Mq9SnAW4NkeTlQdMql_fxBSZAqijMBIx5MMJHx0r-7O47-OYE.7O.dTJAmE2RTOMSPqU0CQvdlof-WmDKkSX7jO0Z4Mnt_ZM9UIrd-A2gUfgVGo3rvOB9W1w7ku3hgMK"),
        encrypt=True,
        sslValidateCertificate=True,
        currentSchema=os.environ.get("HANA_SCHEMA", "43986AB4EB174D8AAB87650958CCA6AD")
    )

def _fetchall(query, params=()):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    cols = [d[0].lower() for d in cur.description]
    rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    conn.close()
    return rows

def _execute(query, params=()):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()

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
    return []

def save_promotion_requests(data):
    pass

def get_project_change_requests():
    return []

def save_project_change_requests(data):
    pass

def disponibilita_risorsa(risorsa_id: str) -> int:
    allocazioni = [a for a in get_allocations() if a.get("risorsa_id") == risorsa_id]
    totale = sum(a.get("percentuale", 0) for a in allocazioni)
    return max(0, 100 - totale)
