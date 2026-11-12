"""Migra le 13 utenze del prototipo (STAFFMATCH_RISORSA) in SM_RISORSA + SM_ACCESS
e crea una storia DEMO plausibile (contratti, opportunity, OSR, skill, certificazioni).

Solo ambiente dev. Tutti i dati inventati hanno prefisso DEMO- e si rimuovono con
`python scripts/migrate_access_dev.py --remove-demo`.
Uso: python scripts/migrate_access_dev.py [--dry-run | --remove-demo]
"""
import json
import sys
from datetime import date

import yaml
from hdbcli import dbapi

MANIFEST = "manifest-dev.yml"
EID_BASE = 990000

LEVEL_BY_ROLE = {
    "RU001": (11, "Analyst"), "RU002": (11, "Analyst"), "RU003": (10, "Senior Analyst"),
    "RU004": (11, "Analyst"), "RU005": (10, "Senior Analyst"), "RU006": (9, "Consultant"),
    "RU007": (9, "Consultant"), "RU008": (8, "Associate Manager"), "RU009": (8, "Associate Manager"),
    "RU010": (7, "Manager"), "RU011": (7, "Manager"), "RU012": (5, "Associate Director"),
}
LEVEL_OVERRIDE = {"R011": (6, "Senior Manager")}
YEARS_BY_LEVEL = {5: 16, 6: 14, 7: 11, 8: 8, 9: 5, 10: 3, 11: 1}
LANG_CODE = {"italiano": "ITA", "inglese": "ENG", "tedesco": "DEU", "francese": "FRA", "spagnolo": "ESP"}

SKILLS = {
    "R001": ["SAP Analytics Cloud", "SAP Datasphere", "SQL", "Agile/Scrum"],
    "R002": ["Power BI", "SAP Analytics Cloud", "SQL"],
    "R003": ["Databricks", "Python", "SQL", "Apache Spark", "Azure Data Factory"],
    "R004": ["SAP BW4", "SAP HANA", "SQL"],
    "R005": ["Agile/Scrum", "Azure DevOps"],
    "R006": ["Databricks", "Python", "Snowflake", "dbt"],
    "R007": ["Python", "Apache Spark", "Terraform", "SAP Integration Suite"],
    "R008": ["Power BI", "Tableau", "SQL"],
    "R009": ["Agile/Scrum"],
    "R010": ["SAP BW4", "SAP ABAP", "SAP HANA"],
    "R011": ["Agile/Scrum", "Azure DevOps"],
    "REE744F15": ["SQL"],
}

# legacy id -> [(cert_id, city, expiration)]
CERTS = {
    "R001": [("CERT-004", "Milano", date(2027, 5, 20)), ("CERT-003", "Milano", date(2027, 9, 10))],
    "R002": [("CERT-004", "Torino", date(2026, 12, 1))],
    "R003": [("CERT-002", "Roma", date(2027, 7, 16))],
    "R004": [("CERT-001", "Bologna", date(2027, 3, 4)), ("CERT-003", "Bologna", date(2027, 8, 30))],
    "R006": [("CERT-005", "Padova", date(2027, 6, 18))],
    "R007": [("CERT-014", "Roma", date(2027, 7, 22))],
    "R010": [("CERT-002", "Bari", date(2027, 2, 12))],
}

D = date
CONTRACTS = [
    ("CNT-DEMO-001", "SAP Analytics Cloud Planning Rollout — Apex Automotive GmbH", "Apex Automotive GmbH",
     "Manufacturing", "DEU", "PRD-Ind/mob/CG&S", "M. Lombardi", D(2026, 3, 1), D(2027, 3, 31), 480000, 330000, "R005"),
    ("CNT-DEMO-002", "Datasphere Data Platform — Aurora Bank SpA", "Aurora Bank SpA",
     "Financial Services", "ITA", "FS", "N. Moretti", D(2026, 6, 1), D(2027, 6, 30), 650000, 450000, "R011"),
    ("CNT-DEMO-003", "AI Core Forecasting — Orion Energy Srl", "Orion Energy Srl",
     "Energy", "ITA", "RES", "P. Costa", D(2026, 9, 1), D(2027, 2, 28), 310000, 210000, "R009"),
    ("CNT-DEMO-004", "BW4 Migration Wrap-up — Atlas Oil & Gas SpA", "Atlas Oil & Gas SpA",
     "Energy", "ITA", "RES", "O. Gallo", D(2025, 10, 1), D(2026, 12, 5), 220000, 175000, "R005"),
]
OPPORTUNITIES = [
    ("OPP-DEMO-001", "SAC Planning Implementation — Apex Automotive", "CNT-DEMO-001", "Won", "SAP Analytics Cloud",
     "Finance", D(2026, 3, 1), D(2026, 12, 31), 300000, "Active"),
    ("OPP-DEMO-002", "SAC Reporting Extension — Apex Automotive", "CNT-DEMO-001", "Won", "SAP Analytics Cloud",
     "Operations", D(2026, 9, 1), D(2027, 3, 31), 180000, "Active"),
    ("OPP-DEMO-003", "Datasphere Core Layer — Aurora Bank", "CNT-DEMO-002", "Won", "SAP Datasphere/BDC",
     "Finance", D(2026, 6, 1), D(2027, 3, 31), 400000, "Active"),
    ("OPP-DEMO-004", "Power BI Regulatory Dashboards — Aurora Bank", "CNT-DEMO-002", "Won", "Microsoft PBI/Fabric",
     "Finance", D(2026, 9, 15), D(2027, 6, 30), 250000, "Active"),
    ("OPP-DEMO-005", "AI Demand Forecasting — Orion Energy", "CNT-DEMO-003", "Won", "SAP AI Core",
     "Operations", D(2026, 9, 1), D(2027, 2, 28), 310000, "Active"),
    ("OPP-DEMO-006", "BW4 Decommissioning — Atlas Oil & Gas", "CNT-DEMO-004", "Won", "SAP BW4/HANA",
     "Finance", D(2025, 10, 1), D(2026, 12, 5), 220000, "Active"),
    ("OPP-DEMO-007", "AI Claims Triage — Aurora Bank", "CNT-DEMO-002", "Open", "SAP AI Core",
     "HR", D(2027, 1, 10), D(2027, 9, 30), 150000, "Pipeline"),
]
# (legacy id, opportunity, role, perc, start, end)
OSRS = [
    ("R001", "OPP-DEMO-001", "Solution Architect", 60, D(2026, 3, 1), D(2026, 12, 31)),
    ("R002", "OPP-DEMO-001", "BI Developer", 60, D(2026, 3, 1), D(2026, 12, 31)),
    ("R004", "OPP-DEMO-001", "Business Analyst", 50, D(2026, 3, 1), D(2026, 12, 31)),
    ("R005", "OPP-DEMO-001", "Project Manager", 30, D(2026, 3, 1), D(2026, 12, 31)),
    ("R001", "OPP-DEMO-002", "Solution Architect", 40, D(2026, 9, 1), D(2027, 3, 31)),
    ("R010", "OPP-DEMO-002", "BI Developer", 80, D(2026, 9, 1), D(2027, 3, 31)),
    ("R003", "OPP-DEMO-003", "Data Engineer", 100, D(2026, 6, 1), D(2027, 3, 31)),
    ("R006", "OPP-DEMO-003", "Databricks Engineer", 100, D(2026, 6, 1), D(2027, 3, 31)),
    ("R007", "OPP-DEMO-003", "Tech Lead", 50, D(2026, 6, 1), D(2027, 3, 31)),
    ("R011", "OPP-DEMO-003", "Project Manager", 20, D(2026, 6, 1), D(2027, 3, 31)),
    ("R002", "OPP-DEMO-004", "BI Developer", 40, D(2026, 9, 15), D(2027, 6, 30)),
    ("R008", "OPP-DEMO-004", "Business Analyst", 100, D(2026, 9, 15), D(2027, 6, 30)),
    ("R004", "OPP-DEMO-004", "Business Analyst", 50, D(2026, 9, 15), D(2027, 6, 30)),
    ("R009", "OPP-DEMO-005", "Project Manager", 30, D(2026, 9, 1), D(2027, 2, 28)),
    ("R007", "OPP-DEMO-005", "ML Engineer", 50, D(2026, 9, 1), D(2027, 2, 28)),
    ("R005", "OPP-DEMO-006", "Project Manager", 20, D(2025, 10, 1), D(2026, 12, 5)),
    ("R010", "OPP-DEMO-006", "SAP BW4/HANA Developer", 20, D(2025, 10, 1), D(2026, 12, 5)),
]


def connect():
    manifest = yaml.safe_load(open(MANIFEST))
    env = next(a for a in manifest["applications"] if "backend" in a["name"])["env"]
    conn = dbapi.connect(
        address=env["HANA_ADDRESS"], port=int(env["HANA_PORT"]), user=env["HANA_USER"],
        password=env["HANA_PASSWORD"], encrypt=True, sslValidateCertificate=False,
        currentSchema=env["HANA_SCHEMA"],
    )
    conn.setautocommit(False)
    return conn


def insert(cur, table, row):
    cur.execute(
        "SELECT COLUMN_NAME FROM TABLE_COLUMNS WHERE SCHEMA_NAME = CURRENT_SCHEMA AND TABLE_NAME = ?",
        (table,),
    )
    live = {r[0] for r in cur.fetchall()}
    cols = {k.upper(): v for k, v in row.items()}
    unknown = set(cols) - live
    if unknown:
        raise RuntimeError(f"{table}: colonne sconosciute {unknown}")
    names = ", ".join(f'"{c}"' for c in cols)
    marks = ", ".join("?" for _ in cols)
    cur.execute(f'INSERT INTO "{table}" ({names}) VALUES ({marks})', tuple(cols.values()))


def remove_demo(cur):
    cur.execute("SELECT EID FROM STAFFMATCH_SM_ACCESS WHERE EID >= ?", (EID_BASE,))
    eids = [r[0] for r in cur.fetchall()]
    cur.execute("DELETE FROM STAFFMATCH_SM_OSR WHERE OSRID LIKE 'OSR-DEMO-%'")
    cur.execute("DELETE FROM STAFFMATCH_SM_OPPORTUNITY WHERE OPPORTUNITYID LIKE 'OPP-DEMO-%'")
    cur.execute("DELETE FROM STAFFMATCH_SM_CONTRACT WHERE CONTRACTID LIKE 'CNT-DEMO-%'")
    for eid in eids:
        cur.execute("DELETE FROM STAFFMATCH_SM_RISORSACERT WHERE EMAIL IN (SELECT EMAIL FROM STAFFMATCH_SM_RISORSA WHERE EID = ?)", (eid,))
        for t in ("SM_RISORSASKILL", "SM_RISORSALANGUAGE", "SM_RISORSA", "SM_ACCESS"):
            cur.execute(f"DELETE FROM STAFFMATCH_{t} WHERE EID = ?", (eid,))
    print(f"Rimossi dati DEMO e {len(eids)} utenze migrate")


def migrate(cur):
    cur.execute("SELECT COUNT(*) FROM STAFFMATCH_SM_ACCESS")
    if cur.fetchone()[0]:
        raise SystemExit("SM_ACCESS non è vuota: migrazione già eseguita, nulla da fare.")

    cur.execute("SELECT ID, NOME FROM STAFFMATCH_GRUPPORUOLO")
    group_name = dict(cur.fetchall())
    cur.execute(
        "SELECT ID, NOME, COGNOME, EMAIL, RUOLOID, LINGUE, ISACTIVE, PASSWORDHASH, GRUPPORUOLOIDS, "
        "DISPONIBILITA, STAGISTA FROM STAFFMATCH_RISORSA ORDER BY ID"
    )
    legacy = cur.fetchall()

    cur.execute("SELECT CERTID, NOMECERT FROM STAFFMATCH_SM_CERTCATALOG")
    cert_name = dict(cur.fetchall())

    eid_of, email_of, level_of = {}, {}, {}
    for idx, (rid, nome, cognome, email, ruolo, lingue, active, pwd, groups, disp, stagista) in enumerate(legacy):
        eid = EID_BASE + idx
        email = email.lower()
        level, level_name = LEVEL_OVERRIDE.get(rid) or LEVEL_BY_ROLE[ruolo]
        eid_of[rid], email_of[rid], level_of[rid] = eid, email, (level, level_name)

        insert(cur, "STAFFMATCH_SM_RISORSA", {
            "eid": eid, "nome": nome, "cognome": cognome, "email": email, "level": level,
            "levelName": level_name, "anniEsperienza": YEARS_BY_LEVEL[level],
            "disponibilita": disp, "isStagista": bool(stagista),
        })
        group = group_name[json.loads(groups)[0]]
        insert(cur, "STAFFMATCH_SM_ACCESS", {
            "email": email, "nome": nome, "cognome": cognome, "passwordHash": pwd,
            "accessGroup": group, "isActive": bool(active), "mustChangePassword": False, "eid": eid,
        })
        for lang in json.loads(lingue or "[]"):
            insert(cur, "STAFFMATCH_SM_RISORSALANGUAGE", {"eid": eid, "languageCode": LANG_CODE[lang]})
        for skill in SKILLS.get(rid, []):
            insert(cur, "STAFFMATCH_SM_RISORSASKILL", {"eid": eid, "skillName": skill})
        for cert_id, city, exp in CERTS.get(rid, []):
            insert(cur, "STAFFMATCH_SM_RISORSACERT", {
                "email": email, "certId": cert_id, "nomeCert": cert_name[cert_id], "city": city,
                "level": level, "levelName": level_name, "expirationDate": exp,
            })

    for cid, title, client, industry, country, group, lead, start, end, rev, cost, mgr in CONTRACTS:
        mgr_row = next(r for r in legacy if r[0] == mgr)
        insert(cur, "STAFFMATCH_SM_CONTRACT", {
            "contractId": cid, "contractTitle": title, "clientName": client, "industrySector": industry,
            "country": country, "contractManager": f"{mgr_row[1]} {mgr_row[2]}", "serviceGroup": group,
            "practiceLead": lead, "dataInizio": start, "dataFine": end, "contractRevenue": rev, "costi": cost,
            "contractStatus": "Active", "isCrossPractice": False, "daPracticePct": 100, "eid": eid_of[mgr],
        })
    for oid, title, cid, stage, tech, area, start, end, value, status in OPPORTUNITIES:
        insert(cur, "STAFFMATCH_SM_OPPORTUNITY", {
            "opportunityId": oid, "opportunityTitle": title, "contractId": cid, "opportunityStage": stage,
            "mainTechCluster": tech, "functionalArea": area, "dataInizio": start, "dataFine": end,
            "opportunityValue": value, "opportunityStatus": status,
        })
    for n, (rid, opp, role, perc, start, end) in enumerate(OSRS, 1):
        insert(cur, "STAFFMATCH_SM_OSR", {
            "osrId": f"OSR-DEMO-{n:03d}", "eid": eid_of[rid], "opportunityId": opp, "ruoloInProgetto": role,
            "percAllocazione": perc, "chargeabilityPct": perc, "dataInizio": start, "dataFine": end,
            "stato": "Active",
        })
    print(f"Migrate {len(legacy)} utenze, {len(CONTRACTS)} contratti, {len(OPPORTUNITIES)} opportunity, {len(OSRS)} OSR")


if __name__ == "__main__":
    connection = connect()
    cursor = connection.cursor()
    try:
        if "--remove-demo" in sys.argv:
            remove_demo(cursor)
        else:
            migrate(cursor)
        if "--dry-run" in sys.argv:
            connection.rollback()
            print("DRY-RUN: nessuna modifica salvata")
        else:
            connection.commit()
            print("Commit eseguito")
    except Exception:
        connection.rollback()
        raise
