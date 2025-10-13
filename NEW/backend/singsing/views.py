import csv
from pathlib import Path
from django.core.paginator import Paginator
from django.shortcuts import render

CSV_PATH = Path(__file__).resolve().parent / "database" / "DatasetForBackend.csv"

def products(request):
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        return render(request, "products.html", {"headers": [], "page_obj": None})

    headers, data = rows[0], rows[1:]
    idx = {h: i for i, h in enumerate(headers)}  # header -> index

    # -------- FILTERS GO HERE (between data split and pagination) --------
    q         = (request.GET.get("q") or "").strip().lower()
    category  = (request.GET.get("category") or "").strip().lower()
    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")

    def cell(row, col):
        j = idx.get(col)
        return row[j] if j is not None and j < len(row) else ""

    filtered = data
    if q:
        filtered = [r for r in filtered if any(q in str(c).lower() for c in r)]
    if category:
        filtered = [r for r in filtered if cell(r, "Category").strip().lower() == category]

    def to_float(s):
        try: return float(str(s).replace(",", "").strip())
        except: return None
    if price_min or price_max:
        lo = float(price_min) if price_min else None
        hi = float(price_max) if price_max else None
        tmp = []
        for r in filtered:
            v = to_float(cell(r, "Price"))
            if v is None: 
                continue
            if (lo is None or v >= lo) and (hi is None or v <= hi):
                tmp.append(r)
        filtered = tmp
    # -------- END FILTERS --------

    # Now paginate the *filtered* rows
    paginator = Paginator(filtered, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "products.html", {
        "headers": headers,
        "page_obj": page_obj,
        "params": request.GET,  # optional: to preserve filters in links/forms
    })

