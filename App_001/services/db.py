from hdbcli import dbapi

def _get_conn():
    return dbapi.connect(
        address="268718a1-2b08-4eb6-99ec-87a77e84bab0.hna2.prod-eu10.hanacloud.ondemand.com",
        port=443,
        user="43986AB4EB174D8AAB87650958CCA6AD_31OU7WNFBO7Y4JDWIWL6COUSQ_RT",
        password="Mq9SnAW4NkeTlQdMql_fxBSZAqijMBIx5MMJHx0r-7O47-OYE.7O.dTJAmE2RTOMSPqU0CQvdlof-WmDKkSX7jO0Z4Mnt_ZM9UIrd-A2gUfgVGo3rvOB9W1w7ku3hgMK",
        encrypt=True,
        sslValidateCertificate=True,
        currentSchema="43986AB4EB174D8AAB87650958CCA6AD"
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
    rows = _fetchall("SELECT ID, CODICE, DESCRIZIONE, LIVELLOMIN, LIVELLOMAX FROM STAFFMATCH_SKILL")
    return [{"id": r["id"], "nome": r["codice"], "descrizione": r["descrizione"], "livello_min": r["livellomin"], "livello_max": r["livellomax"]} for r in rows]

def save_skills(data):
    _execute("DELETE FROM STAFFMATCH_SKILL")
    for s in data:
        _execute("INSERT INTO STAFFMATCH_SKILL (ID, CODICE, DESCRIZIONE, LIVELLOMIN, LIVELLOMAX) VALUES (?,?,?,?,?)",
                 (s.get("id"), s.get("nome"), s.get("descrizione"), s.get("livello_min"), s.get("livello_max")))

def get_roles():
    return _fetchall("SELECT ID, NOME, LIVELLO, DESCRIZIONE FROM STAFFMATCH_MANSIONE")

def save_roles(data):
    _execute("DELETE FROM STAFFMATCH_MANSIONE")
    for r in data:
        _execute("INSERT INTO STAFFMATCH_MANSIONE (ID, NOME, LIVELLO, DESCRIZIONE) VALUES (?,?,?,?)",
                 (r.get("id"), r.get("nome"), r.get("livello"), r.get("descrizione")))

def get_role_groups():
    return []

def save_role_groups(data):
    pass

def get_resources():
    risorse = _fetchall("SELECT * FROM STAFFMATCH_RISORSA")
    for r in risorse:
        r["skills"] = _fetchall("SELECT SKILL_ID, LIVELLO FROM STAFFMATCH_RISORSASKILL WHERE RISORSA_ID = ?", (r["id"],))
        r["costo_orario"] = r.pop("costoorario", None)
        r["termine_progetto"] = r.pop("termineprogetto", None)
        r["movimento_in_corso"] = r.pop("movimentoincorso", None)
    return risorse

def save_resources(data):
    _execute("DELETE FROM STAFFMATCH_RISORSASKILL")
    _execute("DELETE FROM STAFFMATCH_RISORSA")
    for r in data:
        _execute("INSERT INTO STAFFMATCH_RISORSA (ID, NOME, COGNOME, EMAIL, MANSIONE_ID, LIVELLO, COSTOORARIO, DISPONIBILITA, TERMINEPROGETTO, OFFSHORE, STAGISTA, MOVIMENTOINCORSO, LINGUA) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                 (r.get("id"), r.get("nome"), r.get("cognome"), r.get("email"), r.get("mansione_id"), r.get("livello"), r.get("costo_orario"), r.get("disponibilita"), r.get("termine_progetto"), r.get("offshore"), r.get("stagista"), r.get("movimento_in_corso"), r.get("lingua")))
        for sk in r.get("skills", []):
            _execute("INSERT INTO STAFFMATCH_RISORSASKILL (RISORSA_ID, SKILL_ID, LIVELLO) VALUES (?,?,?)",
                     (r.get("id"), sk.get("skill_id"), sk.get("livello")))

def get_opportunities():
    needs = _fetchall("SELECT * FROM STAFFMATCH_NEED")
    result = []
    for n in needs:
        n["titolo_progetto"] = n.pop("iniziativa", None)
        n["data_avvio"] = n.pop("dataavvio", None)
        n["attiva"] = n.pop("ipotesi", True)
        n["skills_richieste"] = _fetchall("SELECT SKILL_ID, LIVELLOMINIMO FROM STAFFMATCH_NEEDSKILL WHERE NEED_ID = ?", (n["id"],))
        result.append(n)
    return result

def save_opportunities(data):
    _execute("DELETE FROM STAFFMATCH_NEEDSKILL")
    _execute("DELETE FROM STAFFMATCH_NEED")
    for o in data:
        _execute("INSERT INTO STAFFMATCH_NEED (ID, CLIENTE, INIZIATIVA, DESCRIZIONE, OSR, DATAAVVIO, PRIORITA, STATUS, IPOTESI) VALUES (?,?,?,?,?,?,?,?,?)",
                 (o.get("id"), o.get("cliente"), o.get("titolo_progetto"), o.get("descrizione"), o.get("osr"), o.get("data_avvio"), o.get("priorita"), o.get("status"), o.get("attiva", True)))
        for sk in o.get("skills_richieste", []):
            _execute("INSERT INTO STAFFMATCH_NEEDSKILL (NEED_ID, SKILL_ID, LIVELLO_MIN) VALUES (?,?,?)",
                     (o.get("id"), sk.get("skill_id"), sk.get("livellominimo")))

def get_allocations():
    return _fetchall("SELECT * FROM STAFFMATCH_ALLOCAZIONE")

def save_allocations(data):
    _execute("DELETE FROM STAFFMATCH_ALLOCAZIONE")
    for a in data:
        _execute("INSERT INTO STAFFMATCH_ALLOCAZIONE (ID, RISORSA_ID, NEED_ID, PERCENTUALE, DATASTART, DATAEND, STATUS) VALUES (?,?,?,?,?,?,?)",
                 (a.get("id"), a.get("risorsa_id"), a.get("need_id"), a.get("percentuale"), a.get("data_start"), a.get("data_end"), a.get("status")))

def get_match_results():
    return _fetchall("SELECT * FROM STAFFMATCH_MATCHRESULT")

def save_match_results(data):
    _execute("DELETE FROM STAFFMATCH_MATCHRESULT")
    for m in data:
        _execute("INSERT INTO STAFFMATCH_MATCHRESULT (ID, NEED_ID, RISORSA_ID, SCORE, MOTIVAZIONE, CREATEDAT) VALUES (?,?,?,?,?,?)",
                 (m.get("id"), m.get("need_id"), m.get("risorsa_id"), m.get("score"), m.get("motivazione"), m.get("created_at")))

def get_projects():
    return get_opportunities()

def save_projects(data):
    pass

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
