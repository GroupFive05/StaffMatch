from datetime import date, datetime

FY_START_MONTH = 9


def fy_of(year, month):
    return year + 1 if month >= FY_START_MONTH else year


def current_fy(today=None):
    today = today or date.today()
    return fy_of(today.year, today.month)


def fy_label(fy):
    return f"FY{fy}"


def fy_period_text(fy):
    return f"Sep {fy - 1} – Aug {fy}"


def parse_date(value):
    if value in (None, ""):
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def month_index(value):
    return value.year * 12 + value.month - 1


def fy_share(amount, start, end, fy):
    """Quota dell'importo di competenza del fiscal year `fy`.

    L'importo è mensilizzato: totale / mesi di calendario del periodo (primo e
    ultimo mese inclusi, mese parziale = mese intero) e assegnato al FY di ogni mese.
    """
    start, end = parse_date(start), parse_date(end)

    if start is None or end is None or end < start:
        return 0.0

    first, last = month_index(start), month_index(end)
    total_months = last - first + 1

    fy_first = month_index(date(fy - 1, FY_START_MONTH, 1))
    fy_last = fy_first + 11

    overlap = max(0, min(last, fy_last) - max(first, fy_first) + 1)

    return float(amount or 0) * overlap / total_months


def fy_sum(rows, amount_fn, start_fn, end_fn, fy):
    return sum(fy_share(amount_fn(row), start_fn(row), end_fn(row), fy) for row in rows)


def available_fys(date_values, today=None):
    years = {current_fy(today)}

    for value in date_values:
        parsed = parse_date(value)

        if parsed:
            years.add(fy_of(parsed.year, parsed.month))

    return list(range(min(years), max(years) + 1))


def delta_info(current, previous, fy):
    """Dati di confronto con l'anno fiscale precedente (anno intero contro anno intero)."""
    previous_label = fy_label(fy - 1)

    if not previous:
        pct = None
    else:
        pct = (current / previous - 1) * 100

    return {"pct": pct, "previous": previous, "previous_label": previous_label}
