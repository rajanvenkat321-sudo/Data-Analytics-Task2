
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")          
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches

try:
    import seaborn as sns
    sns.set_theme(style="darkgrid", palette="muted")
    _SEABORN = True
except ImportError:
    _SEABORN = False

try:
    import mysql.connector  # type: ignore[import-not-found]
    from mysql.connector import Error as MySQLError  # type: ignore[import-not-found]
    _MYSQL_AVAILABLE = True
except ImportError:
    _MYSQL_AVAILABLE = False
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root", 
    "password": "rajan@8265746578",          
    "database": "sales_analytics_db",
}

TABLE    = "sales_data"
CSV_PATH = "Cleaned_Sales_Dataset.csv"

# Chart colour palette (accessible & vivid)
PALETTE = [
    "#4C72B0", "#DD8452", "#55A868", "#C44E52",
    "#8172B3", "#937860", "#DA8BC3", "#8C8C8C",
]

ACCENT   = "#4C72B0"
BG_COLOR = "#F8F9FA"


# ──────────────────────────────────────────────────────────
#  UTILITY : section header printer
# ──────────────────────────────────────────────────────────
def _banner(title: str) -> None:
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


# ──────────────────────────────────────────────────────────
#  1.  DATA LOADING
# ──────────────────────────────────────────────────────────
def load_data() -> pd.DataFrame:
    """
    Try MySQL first; fall back to CSV if unavailable / connection fails.
    Returns a cleaned DataFrame.
    """
    df = None

    if _MYSQL_AVAILABLE:
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            if conn.is_connected():
                print("[INFO] Connected to MySQL – reading sales_data …")
                df = pd.read_sql(f"SELECT * FROM `{TABLE}`;", conn)
                conn.close()
                print(f"[OK]   Loaded {len(df):,} rows from MySQL.")
        except Exception as exc:
            print(f"[WARN] MySQL unavailable ({exc}); falling back to CSV.")

    if df is None:
        if not os.path.exists(CSV_PATH):
            print(f"[ERROR] '{CSV_PATH}' not found. Aborting.")
            sys.exit(1)
        print(f"[INFO] Reading '{CSV_PATH}' …")
        df = pd.read_csv(CSV_PATH)
        print(f"[OK]   Loaded {len(df):,} rows from CSV.")

    # ── Coerce types ─────────────────────────────
    df["Order_Date"]  = pd.to_datetime(df["Order_Date"],  errors="coerce")
    df["Age"]         = pd.to_numeric(df["Age"],          errors="coerce")
    df["Quantity"]    = pd.to_numeric(df["Quantity"],     errors="coerce")
    df["Unit_Price"]  = pd.to_numeric(df["Unit_Price"],   errors="coerce")
    df["Total_Sales"] = pd.to_numeric(df["Total_Sales"],  errors="coerce")

    return df


# ──────────────────────────────────────────────────────────
#  2.  EDA SECTIONS
# ──────────────────────────────────────────────────────────
def dataset_summary(df: pd.DataFrame) -> None:
    _banner("DATASET SUMMARY")
    print(f"  Shape          : {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"  Columns        : {list(df.columns)}")
    print(f"  Date range     : {df['Order_Date'].min().date()} → "
          f"{df['Order_Date'].max().date()}")
    print(f"  Cities covered : {df['City'].nunique()} "
          f"({', '.join(sorted(df['City'].unique()))})")
    print(f"  Categories     : {df['Category'].nunique()} "
          f"({', '.join(sorted(df['Category'].unique()))})")
    print(f"  Products       : {df['Product'].nunique()} "
          f"({', '.join(sorted(df['Product'].unique()))})")


def missing_value_analysis(df: pd.DataFrame) -> None:
    _banner("MISSING VALUE ANALYSIS")
    missing = df.isnull().sum()
    pct     = (missing / len(df) * 100).round(2)
    report  = pd.DataFrame({"Missing Count": missing, "Missing %": pct})
    report  = report[report["Missing Count"] > 0]
    if report.empty:
        print("  [OK] No missing values found – dataset is complete.")
    else:
        print(report.to_string())


def descriptive_statistics(df: pd.DataFrame) -> None:
    _banner("DESCRIPTIVE STATISTICS (Numeric Columns)")
    stats = df[["Age", "Quantity", "Unit_Price", "Total_Sales"]].describe()
    print(stats.to_string())


def category_analysis(df: pd.DataFrame) -> pd.Series:
    _banner("CATEGORY-WISE SALES ANALYSIS")
    cat = df.groupby("Category")["Total_Sales"].agg(
        Total_Revenue="sum",
        Avg_Order="mean",
        Orders="count",
    ).sort_values("Total_Revenue", ascending=False)
    cat["Total_Revenue"] = cat["Total_Revenue"].map("Rs.{:,.0f}".format)
    cat["Avg_Order"]     = cat["Avg_Order"].map("Rs.{:,.0f}".format)
    print(cat.to_string())
    return df.groupby("Category")["Total_Sales"].sum().sort_values(ascending=False)


def city_analysis(df: pd.DataFrame) -> pd.Series:
    _banner("CITY-WISE SALES ANALYSIS")
    city = df.groupby("City")["Total_Sales"].agg(
        Total_Revenue="sum",
        Avg_Order="mean",
        Orders="count",
    ).sort_values("Total_Revenue", ascending=False)
    city["Total_Revenue"] = city["Total_Revenue"].map("Rs.{:,.0f}".format)
    city["Avg_Order"]     = city["Avg_Order"].map("Rs.{:,.0f}".format)
    print(city.to_string())
    return df.groupby("City")["Total_Sales"].sum().sort_values(ascending=False)


def product_analysis(df: pd.DataFrame) -> None:
    _banner("PRODUCT PERFORMANCE ANALYSIS")
    prod = df.groupby("Product").agg(
        Revenue=("Total_Sales", "sum"),
        Units_Sold=("Quantity",    "sum"),
        Orders=("Order_ID",  "count"),
    ).sort_values("Revenue", ascending=False)
    prod["Revenue"] = prod["Revenue"].map("Rs.{:,.0f}".format)
    print(prod.to_string())


def monthly_trend(df: pd.DataFrame) -> pd.Series:
    _banner("MONTHLY SALES TREND ANALYSIS")
    month_names = {
        1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
        7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"
    }
    monthly = (
        df.assign(Month=df["Order_Date"].dt.month)
          .groupby("Month")["Total_Sales"].sum()
          .reindex(range(1, 13), fill_value=0)
    )
    monthly.index = monthly.index.map(month_names)
    print(monthly.map("Rs.{:,.0f}".format).to_string())
    return monthly


def age_distribution(df: pd.DataFrame) -> None:
    _banner("CUSTOMER AGE DISTRIBUTION ANALYSIS")
    bins   = [0, 20, 30, 40, 50, 60, 70]
    labels = ["<20", "20-29", "30-39", "40-49", "50-59", "60+"]
    groups = pd.cut(df["Age"].dropna(), bins=bins, labels=labels, right=False)
    print(groups.value_counts().sort_index().to_string())


def _style_axes(ax, title: str, xlabel: str, ylabel: str) -> None:
    """Apply consistent, attractive formatting to an axis."""
    ax.set_title(title, fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel(xlabel, fontsize=11, labelpad=8)
    ax.set_ylabel(ylabel, fontsize=11, labelpad=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="both", labelsize=10)


def chart_sales_by_category(df: pd.DataFrame) -> None:
    """Horizontal bar chart – Sales by Category."""
    cat_sales = df.groupby("Category")["Total_Sales"].sum().sort_values()

    fig, ax = plt.subplots(figsize=(10, 5), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    bars = ax.barh(cat_sales.index, cat_sales.values,
                   color=PALETTE[:len(cat_sales)], edgecolor="white",
                   linewidth=0.8, height=0.6)

    # Value labels
    for bar, val in zip(bars, cat_sales.values):
        ax.text(val + cat_sales.max() * 0.01, bar.get_y() + bar.get_height() / 2,
                f"Rs.{val/1e6:.1f}M", va="center", ha="left",
                fontsize=9, fontweight="bold", color="#333")

    ax.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"Rs.{x/1e6:.0f}M"))

    _style_axes(ax, "Revenue by Category", "Total Revenue (Rs.)", "Category")
    plt.tight_layout()
    plt.savefig("sales_by_category.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("[CHART] sales_by_category.png saved.")


def chart_sales_by_city(df: pd.DataFrame) -> None:
    """Vertical bar chart – Sales by City."""
    city_sales = df.groupby("City")["Total_Sales"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(12, 6), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    bars = ax.bar(city_sales.index, city_sales.values,
                  color=PALETTE[:len(city_sales)], edgecolor="white",
                  linewidth=0.8, width=0.6)

    for bar, val in zip(bars, city_sales.values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + city_sales.max() * 0.01,
                f"Rs.{val/1e6:.1f}M", ha="center", va="bottom",
                fontsize=9, fontweight="bold", color="#333")

    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda y, _: f"Rs.{y/1e6:.0f}M"))
    ax.tick_params(axis="x", rotation=30)

    _style_axes(ax, "Revenue by City", "City", "Total Revenue (Rs.)")
    plt.tight_layout()
    plt.savefig("sales_by_city.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("[CHART] sales_by_city.png saved.")


def chart_product_distribution(df: pd.DataFrame) -> None:
    """Pie / donut chart – Product order share."""
    prod_counts = df["Product"].value_counts()

    fig, ax = plt.subplots(figsize=(9, 7), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    # matplotlib 3.8+ returns a PieContainer with named attributes;
    # older versions return a tuple — handle both cases safely.
    pie_result = ax.pie(
        prod_counts,
        labels=None,
        autopct="%1.1f%%",
        colors=PALETTE[:len(prod_counts)],
        startangle=140,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
        pctdistance=0.75,
    )
    # PieContainer (mpl >= 3.8) uses .wedges; autopct texts are at index [2]
    wedges    = pie_result.wedges if hasattr(pie_result, "wedges") else pie_result[0]  # type: ignore[union-attr]
    autotexts = pie_result[2]  # type: ignore[index]  # autopct Text list

    # Donut hole
    centre_circle = plt.Circle((0, 0), 0.50, fc=BG_COLOR)
    ax.add_patch(centre_circle)

    for at in autotexts:
        at.set_fontsize(9)
        at.set_fontweight("bold")

    ax.legend(wedges, prod_counts.index,
              title="Products", loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10)

    ax.set_title("Product Order Distribution", fontsize=15,
                 fontweight="bold", pad=14)
    plt.tight_layout()
    plt.savefig("product_distribution.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("[CHART] product_distribution.png saved.")


def chart_age_distribution(df: pd.DataFrame) -> None:
    """Histogram with KDE – Customer age distribution."""
    ages = df["Age"].dropna()

    fig, ax = plt.subplots(figsize=(10, 5), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    n, bins, patches = ax.hist(ages, bins=20, color=ACCENT,
                                edgecolor="white", linewidth=0.6, alpha=0.85)

    # Colour bars by age group
    for patch, left in zip(patches, bins):
        if left < 25:
            patch.set_facecolor("#55A868")
        elif left < 40:
            patch.set_facecolor("#4C72B0")
        elif left < 55:
            patch.set_facecolor("#DD8452")
        else:
            patch.set_facecolor("#C44E52")

    # KDE overlay
    from scipy.stats import gaussian_kde  # optional, skip if unavailable
    try:
        kde   = gaussian_kde(ages)
        x_kde = np.linspace(ages.min(), ages.max(), 300)
        ax2   = ax.twinx()
        ax2.plot(x_kde, kde(x_kde), color="#333", linewidth=2, linestyle="--",
                 label="KDE")
        ax2.set_ylabel("Density", fontsize=10)
        ax2.spines["top"].set_visible(False)
        ax2.tick_params(axis="y", labelsize=9)
    except Exception:
        pass

    # Legend patches
    legend_patches = [
        mpatches.Patch(color="#55A868", label="< 25"),
        mpatches.Patch(color="#4C72B0", label="25 – 39"),
        mpatches.Patch(color="#DD8452", label="40 – 54"),
        mpatches.Patch(color="#C44E52", label="55 +"),
    ]
    ax.legend(handles=legend_patches, title="Age Groups",
              loc="upper right", fontsize=9)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{int(y):,}"))
    _style_axes(ax, "Customer Age Distribution", "Age", "Number of Orders")
    plt.tight_layout()
    plt.savefig("age_distribution.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("[CHART] age_distribution.png saved.")


def chart_monthly_trend(df: pd.DataFrame) -> None:
    """Line chart with shaded area – Monthly sales trend."""
    month_order = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"]
    monthly = (
        df.assign(Month=df["Order_Date"].dt.month)
          .groupby("Month")["Total_Sales"].sum()
          .reindex(range(1, 13), fill_value=0)
    )
    monthly.index = monthly.index.map(
        dict(enumerate(month_order, start=1)))

    fig, ax = plt.subplots(figsize=(12, 6), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    x_pos = range(len(monthly))
    ax.fill_between(x_pos, monthly.values, alpha=0.18, color=ACCENT)
    ax.plot(x_pos, monthly.values, color=ACCENT, linewidth=2.5,
            marker="o", markersize=8, markerfacecolor="white",
            markeredgewidth=2, markeredgecolor=ACCENT)

    # Annotate each data-point
    for i, (month, val) in enumerate(zip(monthly.index, monthly.values)):
        ax.annotate(
            f"Rs.{val/1e6:.1f}M",
            (i, val),
            textcoords="offset points", xytext=(0, 12),
            ha="center", fontsize=8, fontweight="bold", color="#444"
        )

    ax.set_xticks(list(x_pos))
    ax.set_xticklabels(monthly.index, rotation=30, fontsize=10)
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda y, _: f"Rs.{y/1e6:.0f}M"))

    _style_axes(ax, "Monthly Sales Trend", "Month", "Total Revenue (Rs.)")
    plt.tight_layout()
    plt.savefig("monthly_sales_trend.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("[CHART] monthly_sales_trend.png saved.")


# ──────────────────────────────────────────────────────────
#  4.  BUSINESS INSIGHTS REPORT
# ──────────────────────────────────────────────────────────
def generate_business_insights(df: pd.DataFrame) -> None:
    """Write Business_Insights.md with computed metrics."""
    total_revenue  = df["Total_Sales"].sum()
    total_orders   = len(df)
    avg_order      = total_revenue / total_orders
    top_category   = df.groupby("Category")["Total_Sales"].sum().idxmax()
    top_city       = df.groupby("City")["Total_Sales"].sum().idxmax()
    top_product    = df.groupby("Product")["Total_Sales"].sum().idxmax()
    best_month_num = (
        df.assign(Month=df["Order_Date"].dt.month)
          .groupby("Month")["Total_Sales"].sum().idxmax()
    )
    month_names = {
        1:"January",2:"February",3:"March",4:"April",
        5:"May",6:"June",7:"July",8:"August",
        9:"September",10:"October",11:"November",12:"December"
    }
    best_month = month_names.get(best_month_num, str(best_month_num))

    cat_revenue  = df.groupby("Category")["Total_Sales"].sum().sort_values(ascending=False)
    city_revenue = df.groupby("City")["Total_Sales"].sum().sort_values(ascending=False)
    prod_revenue = df.groupby("Product")["Total_Sales"].sum().sort_values(ascending=False)

    electronics_pct = cat_revenue.get("Electronics", 0) / total_revenue * 100

    report = f"""# Business Insights Report — Sales Analytics (Task 2)

> **Generated:** {pd.Timestamp.now().strftime('%d %B %Y, %H:%M')}
> **Dataset:** Cleaned_Sales_Dataset.csv | **Rows:** {total_orders:,}

---

## 1. Dataset Overview

| Attribute             | Value                                         |
|-----------------------|-----------------------------------------------|
| Total Records         | {total_orders:,}                              |
| Date Range            | {df['Order_Date'].min().date()} → {df['Order_Date'].max().date()} |
| Cities Covered        | {df['City'].nunique()} ({', '.join(sorted(df['City'].unique()))}) |
| Product Categories    | {df['Category'].nunique()} ({', '.join(sorted(df['Category'].unique()))}) |
| Unique Products       | {df['Product'].nunique()} ({', '.join(sorted(df['Product'].unique()))}) |
| Total Revenue         | Rs.{total_revenue:,.2f}                       |
| Average Order Value   | Rs.{avg_order:,.2f}                           |

---

## 2. Key Findings

### Revenue Performance
- **Total Revenue:** Rs.{total_revenue/1e6:.2f} Million
- **Average Order Value:** Rs.{avg_order:,.0f}
- **Total Orders Processed:** {total_orders:,}

### Top Performers
- **Top Category:** {top_category} (Rs.{cat_revenue[top_category]/1e6:.2f}M — {cat_revenue[top_category]/total_revenue*100:.1f}% of revenue)
- **Top City:** {top_city} (Rs.{city_revenue[top_city]/1e6:.2f}M)
- **Top Product:** {top_product} (Rs.{prod_revenue[top_product]/1e6:.2f}M)
- **Best Sales Month:** {best_month}

### Category Revenue Breakdown
| Category   | Revenue (Rs.)      | Share (%) |
|------------|--------------------|-----------|
{chr(10).join(f'| {c:<10} | {v:>18,.0f} | {v/total_revenue*100:>8.1f} |' for c, v in cat_revenue.items())}

### City Revenue Breakdown
| City        | Revenue (Rs.)      |
|-------------|--------------------|
{chr(10).join(f'| {c:<11} | {v:>18,.0f} |' for c, v in city_revenue.items())}

### Product Revenue Breakdown
| Product     | Revenue (Rs.)      |
|-------------|--------------------|
{chr(10).join(f'| {p:<11} | {v:>18,.0f} |' for p, v in prod_revenue.items())}

---

## 3. Business Insights

1. **Electronics dominates** the revenue mix at **{electronics_pct:.1f}%** of total sales.
   Laptops and Mobiles are the primary growth drivers.

2. **{top_city}** leads all cities in revenue — indicating strong purchasing power and
   market penetration. Consider investing in targeted campaigns there.

3. **{best_month}** records peak sales, aligning with festive/seasonal buying behaviour.
   Inventory and logistics should be scaled accordingly.

4. The **18–35 age group** represents a significant buyer segment.
   Digital-first marketing (social media, app-based offers) will yield high ROI.

5. **Fashion (Shoes)** and **Grocery (Rice)** have high order volumes but lower unit prices,
   suggesting volume-driven strategies (bundles, loyalty points) could boost margins.

6. Cities like **Gaya** and **Patna** contribute meaningfully despite smaller market size —
   untapped potential for expansion with targeted regional campaigns.

---

## 4. Recommendations

| Priority | Recommendation                                                                 |
|----------|--------------------------------------------------------------------------------|
| High     | Increase Electronics (Laptop/Mobile) inventory ahead of peak months            |
| High     | Launch targeted campaigns in {top_city} to capitalise on existing demand         |
| Med      | Introduce bundled offers for Fashion & Grocery to improve average order value  |
| Med      | Implement a loyalty/referral programme for the 18–35 age segment               |
| Low      | Expand distribution network in Tier-2 cities (Gaya, Patna) via local partners |
| Low      | Use monthly trend data to plan flash sales during low-demand months            |

---

## 5. Generated Visualisations

| Chart File                  | Description                         |
|-----------------------------|-------------------------------------|
| `sales_by_category.png`     | Horizontal bar chart — Revenue by category   |
| `sales_by_city.png`         | Vertical bar chart — Revenue by city          |
| `product_distribution.png`  | Donut chart — Product order share             |
| `age_distribution.png`      | Histogram + KDE — Customer age distribution   |
| `monthly_sales_trend.png`   | Line chart — Monthly revenue trend            |

---

*Report auto-generated by `eda_analysis.py`*
"""

    with open("Business_Insights.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("[REPORT] Business_Insights.md written.")


# ──────────────────────────────────────────────────────────
#  5.  DASHBOARD KPI SUMMARY
# ──────────────────────────────────────────────────────────
def print_dashboard_kpis(df: pd.DataFrame) -> None:
    """Print a concise dashboard-style KPI block to stdout."""
    total_revenue  = df["Total_Sales"].sum()
    total_orders   = len(df)
    avg_order      = total_revenue / total_orders
    top_product    = df.groupby("Product")["Total_Sales"].sum().idxmax()
    top_city       = df.groupby("City")["Total_Sales"].sum().idxmax()

    _banner("DASHBOARD KPI SUMMARY")
    print(f"  [INR] Total Sales Revenue : Rs.{total_revenue:>15,.2f}")
    print(f"  [ORD] Total Orders        : {total_orders:>15,}")
    print(f"  [AOV] Avg Order Value     : Rs.{avg_order:>15,.2f}")
    print(f"  [TOP] Top Product         : {top_product}")
    print(f"  [CTY] Top City            : {top_city}")


# ──────────────────────────────────────────────────────────
#  6.  MAIN
# ──────────────────────────────────────────────────────────
def main() -> None:
    print("=" * 60)
    print("  EDA Analysis Pipeline  –  Task 2")
    print("=" * 60)

    # ── Load ──────────────────────────────────────
    df = load_data()

    # ── EDA sections ──────────────────────────────
    dataset_summary(df)
    missing_value_analysis(df)
    descriptive_statistics(df)
    category_analysis(df)
    city_analysis(df)
    product_analysis(df)
    monthly_trend(df)
    age_distribution(df)

    # ── Charts ────────────────────────────────────
    _banner("GENERATING CHARTS")
    chart_sales_by_category(df)
    chart_sales_by_city(df)
    chart_product_distribution(df)
    chart_age_distribution(df)
    chart_monthly_trend(df)

    # ── Report ────────────────────────────────────
    _banner("GENERATING BUSINESS INSIGHTS REPORT")
    generate_business_insights(df)

    # ── Dashboard KPIs ────────────────────────────
    print_dashboard_kpis(df)

    print("\n" + "=" * 60)
    print("  ✅  EDA Pipeline completed successfully!")
    print("=" * 60)
    print("\nGenerated files:")
    for f in ["sales_by_category.png", "sales_by_city.png",
              "product_distribution.png", "age_distribution.png",
              "monthly_sales_trend.png", "Business_Insights.md"]:
        print(f"  • {f}")


if __name__ == "__main__":
    main()