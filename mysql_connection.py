import sys
import pandas as pd
import mysql.connector  # type: ignore[import-not-found]
from mysql.connector import Error  # type: ignore[import-not-found]

DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",
    "password": "rajan@8265746578",
    "database": "sales_analytics_db",
}

CSV_PATH = "Cleaned_Sales_Dataset.csv"
TABLE    = "sales_data"


def get_connection(include_db: bool = True) -> mysql.connector.MySQLConnection:
    """Return an active MySQLConnection. Exits on failure."""
    cfg = dict(DB_CONFIG)
    if not include_db:
        cfg.pop("database", None)
    try:
        conn = mysql.connector.connect(**cfg)
        if conn.is_connected():
            return conn
    except Error as exc:
        print(f"[ERROR] Could not connect to MySQL: {exc}")
        sys.exit(1)


def ensure_database(conn: mysql.connector.MySQLConnection) -> None:
    """Create the target database if it does not already exist."""
    cursor = conn.cursor()
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}`"
        " CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    )
    cursor.close()
    print(f"[OK] Database `{DB_CONFIG['database']}` is ready.")


def ensure_table(conn: mysql.connector.MySQLConnection) -> None:
    """Create the sales_data table with indexes if it does not exist."""
    cursor = conn.cursor()
    cursor.execute(f"USE `{DB_CONFIG['database']}`;")
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS `{TABLE}` (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            Order_ID      VARCHAR(20)   NOT NULL,
            Order_Date    DATE,
            Customer_ID   VARCHAR(20),
            Customer_Name VARCHAR(50),
            Age           INT,
            Gender        VARCHAR(10),
            City          VARCHAR(50),
            Product       VARCHAR(100),
            Category      VARCHAR(50),
            Quantity      INT,
            Unit_Price    DECIMAL(12, 2),
            Total_Sales   DECIMAL(14, 2),
            INDEX idx_category   (Category),
            INDEX idx_city       (City),
            INDEX idx_product    (Product),
            INDEX idx_order_date (Order_Date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    conn.commit()
    cursor.close()
    print(f"[OK] Table `{TABLE}` is ready.")


def load_csv_to_mysql(conn: mysql.connector.MySQLConnection,
                      csv_path: str = CSV_PATH) -> int:
    """
    Load CSV data into the sales_data table.
    Truncates the table first to ensure idempotent re-runs.
    Returns the number of rows inserted.
    """
    df = pd.read_csv(csv_path, parse_dates=["Order_Date"])

    df["Age"]         = pd.to_numeric(df["Age"],         errors="coerce").astype("Int64")
    df["Quantity"]    = pd.to_numeric(df["Quantity"],    errors="coerce").astype("Int64")
    df["Unit_Price"]  = pd.to_numeric(df["Unit_Price"],  errors="coerce")
    df["Total_Sales"] = pd.to_numeric(df["Total_Sales"], errors="coerce")
    df["Order_Date"]  = pd.to_datetime(df["Order_Date"], errors="coerce").dt.date
    df = df.where(pd.notnull(df), None)

    cursor = conn.cursor()
    cursor.execute(f"USE `{DB_CONFIG['database']}`;")
    cursor.execute(f"TRUNCATE TABLE `{TABLE}`;")

    insert_sql = f"""
        INSERT INTO `{TABLE}`
            (Order_ID, Order_Date, Customer_ID, Customer_Name,
             Age, Gender, City, Product, Category,
             Quantity, Unit_Price, Total_Sales)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    rows = [
        (
            row["Order_ID"], row["Order_Date"], row["Customer_ID"],
            row["Customer_Name"],
            None if pd.isna(row["Age"])      else int(row["Age"]),
            row["Gender"], row["City"], row["Product"], row["Category"],
            None if pd.isna(row["Quantity"]) else int(row["Quantity"]),
            row["Unit_Price"], row["Total_Sales"],
        )
        for _, row in df.iterrows()
    ]

    cursor.executemany(insert_sql, rows)
    conn.commit()
    inserted = cursor.rowcount
    cursor.close()

    print(f"[OK] Inserted {inserted:,} rows into `{TABLE}`.")
    return inserted


def verify_load(conn: mysql.connector.MySQLConnection) -> None:
    """Print the total row count as a post-load sanity check."""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT COUNT(*) AS total FROM `{TABLE}`;")
    total = cursor.fetchone()["total"]
    cursor.close()
    print(f"[VERIFY] Total rows in `{TABLE}`: {total:,}")


def main() -> None:
    conn = get_connection(include_db=False)
    ensure_database(conn)
    conn.close()

    conn = get_connection(include_db=True)
    ensure_table(conn)
    load_csv_to_mysql(conn)
    verify_load(conn)
    conn.close()

    print("[DONE] MySQL pipeline finished successfully.")


if __name__ == "__main__":
    main()
