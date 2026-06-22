# 📊 ApexPlanet Data Analytics Internship - Task 2
**Exploratory Data Analysis & Business Intelligence**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557c?style=for-the-badge&logo=python&logoColor=white)
![Seaborn](https://img.shields.io/badge/Seaborn-3776AB?style=for-the-badge&logo=python&logoColor=white)

## 📖 Overview
This repository contains the deliverables for **Task 2** of the **ApexPlanet Data Analytics Internship**. The primary focus of this project is to conduct comprehensive Exploratory Data Analysis (EDA) on the cleaned sales dataset and execute business intelligence queries using MySQL and Python.

## 🎯 Business Objective
To extract meaningful insights regarding sales performance, category dominance, geographic trends, and customer demographics to inform strategic business decisions.

---

## 📂 Repository Structure

```text
Task2_Data_Analytics/
│
├── mysql_connection.py           # MySQL setup + CSV → DB loader
├── eda_analysis.py               # Full EDA + chart generation + report
├── sql_queries.sql               # Business SQL queries
├── Business_Insights.md          # Auto-generated insights report
├── README.md                     # Project documentation (You are here)
├── Cleaned_Sales_Dataset.csv     # Source data (1,001 orders)
└── charts/                       # Generated visualizations
    ├── sales_by_category.png
    ├── sales_by_city.png
    ├── product_distribution.png
    ├── age_distribution.png
    ├── monthly_sales_trend.png
    └── dashboard_mockup.png
```

---

## 🚀 Quick Start
### Option A — Run EDA only (no MySQL needed)
```bash
python eda_analysis.py
```
*The script auto-detects MySQL; if unavailable it falls back to the CSV file.*

### Option B — Full MySQL pipeline
1. Start your MySQL server and update credentials in `.py` files.
2. Load the CSV into MySQL: `python mysql_connection.py`
3. Run EDA (will read from MySQL): `python eda_analysis.py`

---

## 📊 Analyses Performed
- **Dataset Summary:** Shape, columns, date range, unique values.
- **Descriptive Stats & Missing Values:** Mean, standard deviation, null checks.
- **Category & City Analysis:** Revenue breakdown across categories and Indian cities.
- **Product Performance:** Revenue and units sold per product.
- **Monthly Trend:** Seasonal revenue trends.
- **Age Distribution:** Customer segmentation using binning and KDE.

---

## 🗄️ SQL Queries Overview
Includes 10 business queries spanning:
- Total Revenue & Average Order Value
- Top 5 Products & Category/City shares
- Monthly Trends & Demographics (Gender, Age)

---

## 🔑 Key Findings
- **Electronics** is the dominant revenue category.
- **Bengaluru / Mumbai** lead in city-level revenue.
- **Mobile & Laptop** are top-grossing individual products.
- Sales peak in **Q4 (Oct–Dec)** — indicating a festive season effect.
- **30–44 age group** is the most active buyer segment.
