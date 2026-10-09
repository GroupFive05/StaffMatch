"""
Copia tutte le tabelle HANA dall'ambiente originale verso dev e prod.
Eseguire localmente: python migrate_data.py
Richiede: pip install hdbcli
"""
from hdbcli import dbapi

HANA_ADDRESS = "268718a1-2b08-4eb6-99ec-87a77e84bab0.hna2.prod-eu10.hanacloud.ondemand.com"
HANA_PORT = 443

SOURCE = {
    "user":     "43986AB4EB174D8AAB87650958CCA6AD_31OU7WNFBO7Y4JDWIWL6COUSQ_RT",
    "password": "Mq9SnAW4NkeTlQdMql_fxBSZAqijMBIx5MMJHx0r-7O47-OYE.7O.dTJAmE2RTOMSPqU0CQvdlof-WmDKkSX7jO0Z4Mnt_ZM9UIrd-A2gUfgVGo3rvOB9W1w7ku3hgMK",
    "schema":   "43986AB4EB174D8AAB87650958CCA6AD",
}
DEV = {
    "user":     "4EACFC48246E43F895FA2DC85F66749A_397A7YDQLMP8TI3ZEI55RWQ5U_RT",
    "password": "Ky1sacl19y710T3F_oH9M0jwEzam3OFI8k9Ylw6X6VHnV97KIpyelarMj8ipQLN3EW2LTHCWXXzr4F6pG7wFNQm92WTzYy8kQ6qf2iKsIDSbtOOn6rMZP6zHk1Kqm_ME",
    "schema":   "4EACFC48246E43F895FA2DC85F66749A",
}
PROD = {
    "user":     "E7B94254BF984C7E82C7429ECDFAF57F_CQ4YJ2S1EN82A5SWXMEHAJU7F_RT",
    "password": "Th9xDYFsRPLbLEthgf8exfbTYPLBuomDtfttMnHu0wthhUJjM7Zb9ss86VXFqONEMNCaqUSwvKzRv0p4gl3_8Av6V_HNuH49VDu4FiSh1NUBsQz0vXQx_EyKoSYuBkyb",
    "schema":   "E7B94254BF984C7E82C7429ECDFAF57F",
}

# Ordine rispettando le dipendenze (FK)
TABLE_ORDER = [
    "STAFFMATCH_SKILL",
    "STAFFMATCH_RUOLO",
    "STAFFMATCH_GRUPPORUOLO",
    "STAFFMATCH_RISORSA",
    "STAFFMATCH_RISORSASKILL",
    "STAFFMATCH_OPPORTUNITY",
    "STAFFMATCH_OPPORTUNITYSKILL",
    "STAFFMATCH_OPPORTUNITYSLOT",
    "STAFFMATCH_PROGETTO",
    "STAFFMATCH_ALLOCAZIONE",
    "STAFFMATCH_MATCHRESULT",
    "STAFFMATCH_PROMOTIONREQUEST",
    "STAFFMATCH_PROJECTCHANGEREQUEST",
]


def connect(cfg):
    return dbapi.connect(
        address=HANA_ADDRESS,
        port=HANA_PORT,
        user=cfg["user"],
        password=cfg["password"],
        encrypt=True,
        sslValidateCertificate=True,
        currentSchema=cfg["schema"],
    )


def read_table(conn, table):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table}")
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    return cols, rows


def write_table(conn, table, cols, rows):
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table}")
    if not rows:
        conn.commit()
        return
    placeholders = ", ".join(["?"] * len(cols))
    col_list = ", ".join(cols)
    sql = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})"
    for row in rows:
        cur.execute(sql, list(row))
    conn.commit()


def migrate(source_conn, target_conn, target_name):
    print(f"\n--- Migrazione verso {target_name} ---")
    for table in TABLE_ORDER:
        cols, rows = read_table(source_conn, table)
        write_table(target_conn, table, cols, rows)
        print(f"  {table}: {len(rows)} righe copiate")
    print(f"--- {target_name} completato ---")


if __name__ == "__main__":
    print("Connessione all'ambiente originale (source)...")
    src = connect(SOURCE)

    print("Connessione a DEV...")
    dev = connect(DEV)
    migrate(src, dev, "DEV")

    print("\nConnessione a PROD...")
    prod_conn = connect(PROD)
    migrate(src, prod_conn, "PROD")

    src.close()
    dev.close()
    prod_conn.close()
    print("\nMigrazione completata.")
