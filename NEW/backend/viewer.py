import csv
from pathlib import Path
from django.core.paginator import Paginator
from django.shortcuts import render

CSV_PATH = Path(__file__).resolve().parent / "data" / "sample.csv"

def csv_table(request):
    # read csv safely (handles BOM and newline issues)
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        return render(request, "csv_table.html", {"headers": [], "page_obj": None})

    headers, data = rows[0], rows[1:]

    # optional pagination (e.g., 50 rows per page)
    paginator = Paginator(data, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "csv_table.html", {
        "headers": headers,
        "page_obj": page_obj,
    })
