from io import BytesIO
import re

from fastapi import APIRouter, File, HTTPException, UploadFile
from openpyxl import load_workbook

from services.db import sm_upsert_osr_delta


router = APIRouter(
    prefix="/api/osr",
    tags=["OSR Import"],
)


COLUMN_ALIASES = {
    "osrid": "osr_id",
    "osr": "osr_id",
    "eid": "eid",
    "opportunityid": "opportunity_id",
    "ruoloinprogetto": "ruolo_in_progetto",
    "roleinproject": "ruolo_in_progetto",
    "percallocazione": "perc_allocazione",
    "allocationpercentage": "perc_allocazione",
    "chargeabilitypct": "chargeability_pct",
    "chargeabilitypercentage": "chargeability_pct",
    "datainizio": "data_inizio",
    "startdate": "data_inizio",
    "datafine": "data_fine",
    "enddate": "data_fine",
}


def normalize_header(value):
    if value is None:
        return ""

    return re.sub(
        r"[^a-z0-9]",
        "",
        str(value).strip().lower()
    )


@router.post("/import")
async def import_osr(
    file: UploadFile = File(...),
    dry_run: bool = True,
):
    filename = file.filename or ""

    if not filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=400,
            detail="Il file deve essere in formato .xlsx",
        )

    try:
        content = await file.read()

        workbook = load_workbook(
            BytesIO(content),
            read_only=True,
            data_only=True,
        )

        worksheet = workbook.active

        raw_headers = next(
            worksheet.iter_rows(
                min_row=1,
                max_row=1,
                values_only=True,
            )
        )

        headers = []

        for header in raw_headers:
            normalized_header = normalize_header(header)

            headers.append(
                COLUMN_ALIASES.get(normalized_header)
            )

        if "osr_id" not in headers:
            raise HTTPException(
                status_code=400,
                detail="Colonna OSRID non trovata nel file",
            )

        rows = []

        for excel_row in worksheet.iter_rows(
            min_row=2,
            values_only=True,
        ):
            row = {}

            for index, value in enumerate(excel_row):
                if index >= len(headers):
                    continue

                canonical_header = headers[index]

                if canonical_header:
                    row[canonical_header] = value

            if any(
                value not in (None, "")
                for value in row.values()
            ):
                rows.append(row)

        result = sm_upsert_osr_delta(
            rows=rows,
            dry_run=dry_run,
        )

        result["filename"] = filename
        result["rows_read"] = len(rows)

        return result

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )