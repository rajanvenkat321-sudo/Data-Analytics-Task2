-- =============================================================
--  sql_queries.sql  –  Data Analytics Task 2
--  Database : sales_analytics_db
--  Table    : sales_data
--  Purpose  : Reference SQL queries for business reporting.
-- =============================================================

USE sales_analytics_db;

-- ─────────────────────────────────────────────────────────────
--  1.  TOTAL REVENUE
--      Sum of all completed orders.
-- ─────────────────────────────────────────────────────────────
SELECT
    ROUND(SUM(Total_Sales), 2)  AS Total_Revenue_INR,
    COUNT(*)                    AS Total_Orders
FROM sales_data;


-- ─────────────────────────────────────────────────────────────
--  2.  AVERAGE ORDER VALUE  (AOV)
--      Mean revenue per transaction.
-- ─────────────────────────────────────────────────────────────
SELECT
    ROUND(AVG(Total_Sales), 2) AS Average_Order_Value_INR
FROM sales_data;


-- ─────────────────────────────────────────────────────────────
--  3.  TOP 5 PRODUCTS BY REVENUE
--      Highest grossing products (useful for inventory priority).
-- ─────────────────────────────────────────────────────────────
SELECT
    Product,
    ROUND(SUM(Total_Sales), 2)  AS Total_Revenue_INR,
    SUM(Quantity)               AS Total_Units_Sold,
    COUNT(*)                    AS Total_Orders
FROM sales_data
GROUP BY Product
ORDER BY Total_Revenue_INR DESC
LIMIT 5;


-- ─────────────────────────────────────────────────────────────
--  4.  REVENUE BY CATEGORY
--      Shows which product category drives the most value.
-- ─────────────────────────────────────────────────────────────
SELECT
    Category,
    ROUND(SUM(Total_Sales), 2)                         AS Total_Revenue_INR,
    ROUND(AVG(Total_Sales), 2)                         AS Avg_Order_Value_INR,
    COUNT(*)                                           AS Total_Orders,
    ROUND(SUM(Total_Sales) * 100.0 /
          (SELECT SUM(Total_Sales) FROM sales_data), 2) AS Revenue_Share_Pct
FROM sales_data
GROUP BY Category
ORDER BY Total_Revenue_INR DESC;


-- ─────────────────────────────────────────────────────────────
--  5.  REVENUE BY CITY
--      Identifies strongest geographic markets.
-- ─────────────────────────────────────────────────────────────
SELECT
    City,
    ROUND(SUM(Total_Sales), 2)  AS Total_Revenue_INR,
    ROUND(AVG(Total_Sales), 2)  AS Avg_Order_Value_INR,
    COUNT(*)                    AS Total_Orders,
    COUNT(DISTINCT Customer_ID) AS Unique_Customers
FROM sales_data
GROUP BY City
ORDER BY Total_Revenue_INR DESC;


-- ─────────────────────────────────────────────────────────────
--  6.  MONTHLY REVENUE TREND
--      Month-by-month breakdown (sorted chronologically).
-- ─────────────────────────────────────────────────────────────
SELECT
    YEAR(Order_Date)            AS Year,
    MONTH(Order_Date)           AS Month_Num,
    DATE_FORMAT(Order_Date,'%b %Y')  AS Month_Label,
    ROUND(SUM(Total_Sales), 2)  AS Monthly_Revenue_INR,
    COUNT(*)                    AS Orders_Count
FROM sales_data
WHERE Order_Date IS NOT NULL
GROUP BY YEAR(Order_Date), MONTH(Order_Date)
ORDER BY Year ASC, Month_Num ASC;


-- ─────────────────────────────────────────────────────────────
--  7.  PRODUCT QUANTITY SOLD
--      Units dispatched per product — supply-chain insight.
-- ─────────────────────────────────────────────────────────────
SELECT
    Product,
    SUM(Quantity)               AS Total_Quantity_Sold,
    ROUND(SUM(Total_Sales), 2)  AS Total_Revenue_INR,
    ROUND(AVG(Unit_Price), 2)   AS Avg_Unit_Price_INR
FROM sales_data
GROUP BY Product
ORDER BY Total_Quantity_Sold DESC;


-- ─────────────────────────────────────────────────────────────
--  8.  GENDER-WISE REVENUE SPLIT
--      Understand buyer demographics.
-- ─────────────────────────────────────────────────────────────
SELECT
    Gender,
    COUNT(*)                    AS Total_Orders,
    ROUND(SUM(Total_Sales), 2)  AS Total_Revenue_INR,
    ROUND(AVG(Total_Sales), 2)  AS Avg_Order_Value_INR
FROM sales_data
GROUP BY Gender
ORDER BY Total_Revenue_INR DESC;


-- ─────────────────────────────────────────────────────────────
--  9.  CUSTOMER AGE-GROUP ANALYSIS
--      Revenue segmented by customer age bands.
-- ─────────────────────────────────────────────────────────────
SELECT
    CASE
        WHEN Age < 20          THEN 'Under 20'
        WHEN Age BETWEEN 20 AND 29 THEN '20 – 29'
        WHEN Age BETWEEN 30 AND 39 THEN '30 – 39'
        WHEN Age BETWEEN 40 AND 49 THEN '40 – 49'
        WHEN Age BETWEEN 50 AND 59 THEN '50 – 59'
        ELSE '60+'
    END                         AS Age_Group,
    COUNT(*)                    AS Total_Orders,
    ROUND(SUM(Total_Sales), 2)  AS Total_Revenue_INR,
    ROUND(AVG(Total_Sales), 2)  AS Avg_Order_Value_INR
FROM sales_data
WHERE Age IS NOT NULL
GROUP BY Age_Group
ORDER BY MIN(Age) ASC;


-- ─────────────────────────────────────────────────────────────
-- 10.  TOP CITY × CATEGORY REVENUE MATRIX
--      Cross-analysis of city performance per product category.
-- ─────────────────────────────────────────────────────────────
SELECT
    City,
    Category,
    ROUND(SUM(Total_Sales), 2) AS Revenue_INR,
    COUNT(*)                   AS Orders
FROM sales_data
GROUP BY City, Category
ORDER BY City ASC, Revenue_INR DESC;
