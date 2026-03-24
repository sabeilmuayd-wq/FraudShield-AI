import sqlite3
import pandas as pd
import os
from datetime import datetime

# إنشاء مجلد البيانات
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DATABASE_PATH = os.path.join(DATA_DIR, "fraudshield.db")

def init_database():
    """إنشاء قاعدة البيانات والجداول"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # جدول المعاملات
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL,
        location TEXT,
        device_type TEXT,
        transaction_time TEXT,
        risk_score INTEGER,
        status TEXT
    )
    ''')
    
    # جدول التنبيهات
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id INTEGER,
        message TEXT,
        timestamp TEXT,
        resolved INTEGER DEFAULT 0
    )
    ''')
    
    # جدول قضايا الاحتيال
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fraud_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT,
        amount REAL,
        description TEXT,
        perpetrators TEXT,
        banks_involved TEXT,
        date TEXT,
        status TEXT
    )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_transaction(amount, location, device_type, transaction_time, risk_score, status):
    """إضافة معاملة جديدة"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO transactions (amount, location, device_type, transaction_time, risk_score, status)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (amount, location, device_type, transaction_time, risk_score, status))
    transaction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return transaction_id

def add_alert(transaction_id, message):
    """إضافة تنبيه"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO alerts (transaction_id, message, timestamp)
    VALUES (?, ?, ?)
    ''', (transaction_id, message, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_alerts(unresolved_only=True):
    """جلب التنبيهات"""
    conn = sqlite3.connect(DATABASE_PATH)
    query = "SELECT * FROM alerts"
    if unresolved_only:
        query += " WHERE resolved = 0"
    query += " ORDER BY timestamp DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def resolve_alert(alert_id):
    """حل التنبيه"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE alerts SET resolved = 1 WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()

def get_transactions(limit=100):
    """جلب المعاملات"""
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query(f"SELECT * FROM transactions ORDER BY id DESC LIMIT {limit}", conn)
    conn.close()
    return df

def get_fraud_cases():
    """جلب قضايا الاحتيال"""
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query("SELECT * FROM fraud_cases ORDER BY date DESC", conn)
    conn.close()
    return df

def add_fraud_case(case_id, amount, description, perpetrators, banks_involved, date, status):
    """إضافة قضية احتيال"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO fraud_cases (case_id, amount, description, perpetrators, banks_involved, date, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (case_id, amount, description, perpetrators, banks_involved, date, status))
    conn.commit()
    conn.close()

def get_stats():
    """جلب الإحصائيات"""
    conn = sqlite3.connect(DATABASE_PATH)
    
    total = pd.read_sql_query("SELECT COUNT(*) as c FROM transactions", conn).iloc[0]['c']
    high_risk = pd.read_sql_query("SELECT COUNT(*) as c FROM transactions WHERE risk_score > 70", conn).iloc[0]['c']
    alerts = pd.read_sql_query("SELECT COUNT(*) as c FROM alerts WHERE resolved = 0", conn).iloc[0]['c']
    fraud_cases = pd.read_sql_query("SELECT COUNT(*) as c FROM fraud_cases", conn).iloc[0]['c']
    
    conn.close()
    
    return {
        "total_transactions": total,
        "high_risk": high_risk,
        "alerts": alerts,
        "fraud_cases": fraud_cases
    }

def add_sample_data():
    """إضافة بيانات تجريبية"""
    # قضية Equity Bank Kigali
    add_fraud_case(
        case_id="FRAUD-2026-001",
        amount=12600000000,
        description="احتيال إلكتروني عبر الحدود استهدف Equity Bank Kigali. 6 متهمين أوغنديين.",
        perpetrators="سليمان موغيشا، إينوك مباغا كازيغي، وآخرون",
        banks_involved="Equity Bank (Kigali), Equity Bank (Uganda)",
        date="2026-02-15",
        status="under_investigation"
    )
    
    # معاملات تجريبية
    add_transaction(5000000, "Kampala", "معروف", datetime.now().isoformat(), 15, "approved")
    add_transaction(47000000, "Kampala", "معروف", datetime.now().isoformat(), 20, "approved")
    
    print("✅ Sample data added")

if __name__ == "__main__":
    init_database()
    add_sample_data()
