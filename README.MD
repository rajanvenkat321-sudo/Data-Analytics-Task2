# 📊 Data Analytics Task 2 — Sales Intelligence Project

> **Stack:** Python · Pandas · Matplotlib · Seaborn · MySQL · SQL

---

## 📁 Project Structure

```
Task2_Data_Analytics/
├── Cleaned_Sales_Dataset.csv     ← Source data (1,001 orders)
├── mysql_connection.py           ← MySQL setup + CSV → DB loader
├── eda_analysis.py               ← Full EDA + chart generation + report
├── sql_queries.sql               ← Business SQL queries
├── Business_Insights.md          ← Auto-generated insights report
├── sales_by_category.png         ← Revenue by product category
├── sales_by_city.png             ← Revenue by city
├── product_distribution.png      ← Product order share (donut)
├── age_distribution.png          ← Customer age histogram + KDE
├── monthly_sales_trend.png       ← Monthly revenue line chart
├── dashboard_mockup.png          ← KPI dashboard layout
└── README.md                     ← This file
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+ required
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install pandas matplotlib seaborn scipy mysql-connector-python
```

### Option A — Run EDA only (no MySQL needed)

```bash
python eda_analysis.py
```

The script auto-detects MySQL; if unavailable it falls back to the CSV file.

### Option B — Full MySQL pipeline

1. Start your MySQL server and update credentials in both `.py` files:
   ```python
   DB_CONFIG = {
       "user":     "root",
       "password": "your_password",
       ...
   }
   ```
2. Load the CSV into MySQL:
   ```bash
   python mysql_connection.py
   ```
3. Run EDA (will now read from MySQL):
   ```bash
   python eda_analysis.py
   ```

---

## 📊 Analyses Performed

| Analysis | Description |
|---|---|
| Dataset Summary | Shape, columns, date range, unique values |
| Missing Values | Per-column null count and percentage |
| Descriptive Stats | Mean, std, min/max for numeric columns |
| Category Analysis | Revenue, avg order value, order count by category |
| City Analysis | Revenue breakdown across 10 Indian cities |
| Product Performance | Revenue + units sold per product |
| Monthly Trend | Month-by-month revenue across the year |
| Age Distribution | Customer age segmentation (binned + KDE) |

---

## 🗄️ SQL Queries Overview

| # | Query | Purpose |
|---|---|---|
| 1 | Total Revenue | Overall sales figure |
| 2 | Average Order Value | Mean transaction value |
| 3 | Top 5 Products | Highest-grossing products |
| 4 | Revenue by Category | Category share analysis |
| 5 | Revenue by City | Geographic market split |
| 6 | Monthly Revenue Trend | Seasonality analysis |
| 7 | Product Quantity Sold | Supply-chain demand signal |
| 8 | Gender-wise Split | Demographic revenue split |
| 9 | Age-Group Analysis | Buyer segment profiling |
| 10 | City × Category Matrix | Cross-dimensional insight |

---

## 📈 Generated Charts

| File | Chart Type | Insight |
|---|---|---|
| `sales_by_category.png` | Horizontal bar | Which category earns most |
| `sales_by_city.png` | Vertical bar | Best-performing cities |
| `product_distribution.png` | Donut chart | Order share per product |
| `age_distribution.png` | Histogram + KDE | Customer age spread |
| `monthly_sales_trend.png` | Line + area | Seasonal sales pattern |
| `dashboard_mockup.png` | Dashboard | KPI summary at a glance |

---

## 🔑 Key Findings

- **Electronics** is the dominant revenue category
- **Bengaluru / Mumbai** lead in city-level revenue
- **Mobile & Laptop** are top-grossing individual products
- Sales peak in **Q4 (Oct–Dec)** — festive season effect
- **30–44 age group** is the most active buyer segment

---

## 📋 Database Schema

```sql
CREATE TABLE sales_data (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    Order_ID      VARCHAR(20),
    Order_Date    DATE,
    Customer_ID   VARCHAR(20),
    Customer_Name VARCHAR(50),
    Age           INT,
    Gender        VARCHAR(10),
    City          VARCHAR(50),
    Product       VARCHAR(100),
    Category      VARCHAR(50),
    Quantity      INT,
    Unit_Price    DECIMAL(12,2),
    Total_Sales   DECIMAL(14,2)
);
```

---

## 🛠️ Dependencies

| Package | Version | Purpose |
|---|---|---|
| pandas | ≥ 1.5 | Data manipulation |
| matplotlib | ≥ 3.6 | Chart generation |
| seaborn | ≥ 0.12 | Chart theming |
| scipy | ≥ 1.9 | KDE in age chart |
| mysql-connector-python | ≥ 8.0 | MySQL connectivity |

---

*Task 2 — Data Analytics Internship Project*
