from datetime import timedelta

import fiscal


def summarize_assignment(current_assignments, last_assignment, today):
    """Stato di assegnazione di una risorsa alla data odierna.

    - assegnata: ha almeno una OSR in corso oggi -> data fine più vicina (e data in cui sarà del tutto libera)
    - libera: nessuna OSR in corso -> libera dal giorno dopo l'ultima fine, con l'ultima assegnazione
    """
    active, upcoming = [], []

    for assignment in current_assignments or []:
        start = fiscal.parse_date(assignment.get("start_date"))
        end = fiscal.parse_date(assignment.get("end_date"))

        if start is None or end is None:
            continue

        if start <= today <= end:
            active.append((end, assignment))
        elif start > today:
            upcoming.append((start, assignment))

    upcoming.sort(key=lambda item: item[0])

    result = {
        "state": "assigned" if active else "free",
        "allocated_pct": 0,
        "active": [],
        "nearest_end": None,
        "fully_free_from": None,
        "free_since": None,
        "last": None,
        "next_start": upcoming[0][0] if upcoming else None,
        "next_assignment": upcoming[0][1] if upcoming else None,
    }

    if active:
        active.sort(key=lambda item: item[0])
        result["active"] = [assignment for _, assignment in active]
        result["allocated_pct"] = min(
            100, sum(int(a.get("allocation_pct") or 0) for _, a in active)
        )
        result["nearest_end"] = active[0][0]
        result["fully_free_from"] = active[-1][0] + timedelta(days=1)
    elif last_assignment:
        last_end = fiscal.parse_date(last_assignment.get("end_date"))
        result["last"] = last_assignment

        if last_end:
            result["free_since"] = last_end + timedelta(days=1)

    return result
