import pandas as pd
from mlxtend.frequent_patterns import apriori, fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder
from pathlib import Path
import json

# =========================
# Paths & basic settings
# =========================
INPUT_XLSX  = "SingSing_categories.xlsx"   # must contain: CUST_INVNO, Category (or Sub-category)
OUTPUT_SQL = "mba_rules.sql"  # not used in this script, but you can export to SQL if desired

ITEM_COL = "Sub-category"      # change to "Sub-category" if desired
RARE_MIN_COUNT = 1000        # minimal rarity filter to avoid ultra-rare noise
MAX_LEN = 3                # keep itemsets up to pairs (A,B). Rules will be 1=>1.

# ---------- helpers ----------
def safe_sheetname(name, used):
    bad = '[]:*?/\\'
    for ch in bad: name = name.replace(ch, '')
    base = name[:31]; out = base; i = 1
    while out in used:
        out = (base[:28] + f"({i})")[:31]; i += 1
    used.add(out); return out

def dedupe_list(xs):
    return sorted(set(x for x in xs if pd.notna(x) and str(x).strip()))

def prep_itemsets_pretty(F, max_len=3):
    if F.empty: return F
    F = F.copy()
    if "len" not in F.columns:
        F["len"] = F["itemsets"].apply(len)
    F = F[F["len"] <= max_len]
    if not F.empty:
        F["itemsets"] = F["itemsets"].apply(lambda s: ", ".join(sorted(list(s))))
    return F

def mine_itemsets(X, miner, min_sup):
    return miner(X, min_support=min_sup, use_colnames=True)

def rules_no_filters_from(F, N, max_len=3):
    """Build ALL 1=>1 rules from itemsets (<= max_len). No metric filtering."""
    if F.empty:
        return pd.DataFrame()
    if "len" not in F.columns:
        F = F.copy(); F["len"] = F["itemsets"].apply(len)
    F2 = F[F["len"] <= max_len]
    if F2.empty:
        return pd.DataFrame()
    R = association_rules(F2, metric="confidence", min_threshold=0.0)  # <-- no filtering
    if R.empty:
        return R
    # keep pair-only (1 item => 1 item)
    #R = R[R["antecedents"].apply(len).eq(1) & R["consequents"].apply(len).eq(1)].copy()
    # allow 1–2 items on the left, 1 on the right; total items ≤ MAX_LEN
    R = R[
        R["antecedents"].apply(len).between(1, MAX_LEN-1)
        & R["consequents"].apply(len).eq(1)
        & (R["antecedents"].apply(len) + R["consequents"].apply(len) <= MAX_LEN)
    ].copy()

    if R.empty:
        return R
    # enrich + pretty
    R["support_count"] = (R["support"] * N).round().astype(int)
    R["coverage"] = R["antecedent support"]
    R["lev_count"] = ((R["support"] - R["antecedent support"]*R["consequent support"]) * N).round().astype(int)
    for c in ["antecedents","consequents"]:
        R[c] = R[c].apply(lambda s: ", ".join(sorted(list(s))))
    # order (purely cosmetic)
    cols = ["antecedents","consequents","support","confidence","lift","leverage","conviction",
            "antecedent support","consequent support","coverage","support_count","lev_count"]
    return R[[c for c in cols if c in R.columns]]

# =========================
# Load & preprocess
# =========================
df = pd.read_excel(INPUT_XLSX, dtype={"CUST_INVNO": str})
req = {"CUST_INVNO", ITEM_COL}
missing = req - set(df.columns)
if missing:
    raise ValueError(f"Missing required columns: {missing}")

df = df.dropna(subset=["CUST_INVNO", ITEM_COL]).copy()

# minimal rarity filter
vc = df[ITEM_COL].value_counts()
keep = vc[vc >= RARE_MIN_COUNT].index
df = df[df[ITEM_COL].isin(keep)].copy()
if df.empty:
    raise ValueError("Everything was filtered by RARE_MIN_COUNT. Lower it (e.g., 2).")

# build transactions & drop baskets with <2 items
transactions = (
    df.groupby("CUST_INVNO")[ITEM_COL]
      .apply(dedupe_list)
      .tolist()
)
transactions = [t for t in transactions if len(t) >= 2]
N = len(transactions)
if N == 0:
    raise ValueError("No baskets with ≥2 items after filtering. Loosen rarity filter.")

# one-hot
te = TransactionEncoder()
X = pd.DataFrame(te.fit(transactions).transform(transactions), columns=te.columns_)

# diagnostics
avg_items = sum(map(len, transactions))/max(1, N)
item_supports = X.mean().sort_values(ascending=False)
top_support = float(item_supports.iloc[0]) if len(item_supports) else 0.0

# ======== auto-tune MIN_SUP (visible) ========
auto_min_sup = max(0.001, min(0.02, 0.5 * max(top_support, 0.02)))
if avg_items < 2.0:
    auto_min_sup = max(0.001, auto_min_sup * 0.5)
elif avg_items < 2.5:
    auto_min_sup = max(0.0015, auto_min_sup * 0.75)

# If you want to force a specific value, uncomment next line:
auto_min_sup = 0.06  # <-- custom min_support

MIN_SUP_USED = auto_min_sup

# ---- print parameters to console ----
print("=== MBA Parameters Used ===")
print(f"ITEM_COL           : {ITEM_COL}")
print(f"RARE_MIN_COUNT     : {RARE_MIN_COUNT}")
print(f"MAX_LEN            : {MAX_LEN}")
print(f"n_baskets          : {N}")
print(f"n_items (after OHE): {X.shape[1]}")
print(f"avg_items/basket   : {avg_items:.2f}")
print(f"top_item_support   : {top_support:.4f}")
print(f"min_support_used   : {MIN_SUP_USED:.4f}")
print("===========================")

# =========================
# Mine BOTH algorithms
# =========================
# FP-Growth
F_fp_all = mine_itemsets(X, fpgrowth, MIN_SUP_USED)
F_fp_pretty = prep_itemsets_pretty(F_fp_all, MAX_LEN)
R_fp = rules_no_filters_from(F_fp_all, N, MAX_LEN)

# Apriori
F_ap_all = mine_itemsets(X, apriori, MIN_SUP_USED)
F_ap_pretty = prep_itemsets_pretty(F_ap_all, MAX_LEN)
R_ap = rules_no_filters_from(F_ap_all, N, MAX_LEN)

def _sql_escape(s: str) -> str:
    # escape single quotes and backslashes for MySQL strings
    return s.replace("\\", "\\\\").replace("'", "\\'")

def _mk_values_rows(records, algo):
    rows = []
    for r in records:
        lhs = ", ".join(r["antecedents"])
        rhs = ", ".join(r["consequents"])
        # nullable metrics (present in most runs, but guard anyway)
        leverage    = r.get("leverage", "NULL")
        conviction  = r.get("conviction", "NULL")
        ante_supp   = r.get("ante_support", "NULL")
        cons_supp   = r.get("cons_support", "NULL")
        support_cnt = r.get("support_count", "NULL")
        lev_cnt     = r.get("lev_count", "NULL")
        lhs_len     = r.get("lhs_len", "NULL")
        rhs_len     = r.get("rhs_len", "NULL")
        rule_len    = r.get("rule_len", "NULL")

        row = (
            f"('{algo}',"
            f"'{_sql_escape(lhs)}','{_sql_escape(rhs)}',"
            f"{r['support']:.10f},{r['confidence']:.10f},{r['lift']:.10f},"
            f"{'NULL' if leverage=='NULL' else f'{leverage:.10f}'},"
            f"{'NULL' if conviction=='NULL' else f'{conviction:.10f}'},"
            f"{'NULL' if ante_supp=='NULL' else f'{ante_supp:.10f}'},"
            f"{'NULL' if cons_supp=='NULL' else f'{cons_supp:.10f}'},"
            f"{support_cnt if support_cnt!='NULL' else 'NULL'},"
            f"{lev_cnt if lev_cnt!='NULL' else 'NULL'},"
            f"{lhs_len if lhs_len!='NULL' else 'NULL'},"
            f"{rhs_len if rhs_len!='NULL' else 'NULL'},"
            f"{rule_len if rule_len!='NULL' else 'NULL'})"
        )
        rows.append(row)
    return rows
# -------------------------
# Convert DataFrames -> records for SQL writer
# -------------------------
def _df_to_records(R, N):
    """Return list[dict] with list-typed LHS/RHS and all metrics present."""
    if R is None or R.empty:
        return []
    R2 = R.copy()

    # Ensure list types for antecedents/consequents
    def to_list(x):
        # if already a set/frozenset
        if isinstance(x, (set, frozenset)):
            return sorted(list(x))
        # if pretty string like "A, B"
        return [t.strip() for t in str(x).split(",") if str(t).strip()]

    R2["antecedents"] = R2["antecedents"].apply(to_list)
    R2["consequents"] = R2["consequents"].apply(to_list)

    # Standardize column names
    if "antecedent support" in R2.columns:
        R2 = R2.rename(columns={"antecedent support": "ante_support"})
    if "consequent support" in R2.columns:
        R2 = R2.rename(columns={"consequent support": "cons_support"})

    # Add counts/lengths if missing
    if "support_count" not in R2.columns:
        R2["support_count"] = (R2["support"] * N).round().astype(int)
    if "lev_count" not in R2.columns:
        R2["lev_count"] = ((R2["support"] - R2.get("ante_support", 0)*R2.get("cons_support", 0)) * N).round().astype(int)

    R2["lhs_len"]  = R2["antecedents"].apply(len)
    R2["rhs_len"]  = R2["consequents"].apply(len)
    R2["rule_len"] = R2["lhs_len"] + R2["rhs_len"]

    keep = [
        "antecedents","consequents","support","confidence","lift","leverage","conviction",
        "ante_support","cons_support","support_count","lev_count","lhs_len","rhs_len","rule_len"
    ]
    # keep only columns that exist
    keep = [c for c in keep if c in R2.columns]
    return R2[keep].to_dict(orient="records")

# Build records for both algos
ap_rules = _df_to_records(R_ap, N)
fp_rules = _df_to_records(R_fp, N)

def _chunks(xs, n):
    for i in range(0, len(xs), n):
        yield xs[i:i+n]

DDL = """-- Auto-generated by MBA script
-- Import this file in phpMyAdmin (SQL tab)
CREATE TABLE IF NOT EXISTS `association_rules` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `algorithm` ENUM('apriori','fpgrowth') NOT NULL,
  `antecedents` TEXT NOT NULL,
  `consequents` TEXT NOT NULL,
  `support` DOUBLE NOT NULL,
  `confidence` DOUBLE NOT NULL,
  `lift` DOUBLE NOT NULL,
  `leverage` DOUBLE NULL,
  `conviction` DOUBLE NULL,
  `ante_support` DOUBLE NULL,
  `cons_support` DOUBLE NULL,
  `support_count` INT NULL,
  `lev_count` INT NULL,
  `lhs_len` TINYINT NULL,
  `rhs_len` TINYINT NULL,
  `rule_len` TINYINT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_alg` (`algorithm`),
  KEY `ix_lift` (`lift`),
  KEY `ix_conf` (`confidence`),
  KEY `ix_support` (`support`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

"""

ap_rows = _mk_values_rows(ap_rules, "apriori")
fp_rows = _mk_values_rows(fp_rules, "fpgrowth")

SQL_PATH = Path(OUTPUT_SQL)          # use your OUTPUT_SQL filename
SQL_PATH.parent.mkdir(parents=True, exist_ok=True)

with SQL_PATH.open("w", encoding="utf-8") as f:
    f.write(DDL)
    for label, rows in (("Apriori", ap_rows), ("FP-Growth", fp_rows)):
        if not rows:
            continue
        # batch inserts to keep statements manageable (e.g., 500 rows per INSERT)
        for batch in _chunks(rows, 500):
            values_sql = ",\n".join(batch)
            f.write(
                "INSERT INTO `association_rules` "
                "(algorithm, antecedents, consequents, support, confidence, lift, "
                "leverage, conviction, ante_support, cons_support, support_count, "
                "lev_count, lhs_len, rhs_len, rule_len)\nVALUES\n"
                + values_sql + ";\n\n"
            )

print("SQL export written to:", OUTPUT_SQL.resolve())