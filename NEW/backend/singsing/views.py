import csv
from pathlib import Path
from django.core.paginator import Paginator
from django.shortcuts import render

CSV_PATH = Path(__file__).resolve().parent / "database" / "DatasetForBackend.csv"

def products(request):
    # Read CSV safely
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        return render(request, "products.html", {"headers": [], "page_obj": None})

    headers, data = rows[0], rows[1:]

    # Paginate: 50 items per page
    paginator = Paginator(data, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "products.html", {
        "headers": headers,
        "page_obj": page_obj,
    })
