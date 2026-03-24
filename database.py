import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random

DATABASE_PATH = "data/fraudshield.db"

def init_database():
    """إنشاء قاعدة البيانات والجداول إذا لم تكن موجودة"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # جدول البنوك
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS banks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        tier TEXT,
        license_date TEXT,
        status TEXT DEFAULT 'active'
    )
    ''')
    
    # جدول العملاء
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bank_id INTEGER,
        name TEXT NOT NULL,
        nin TEXT UNIQUE,
        phone TEXT,
        email TEXT,
        account_number TEXT UNIQUE,
        risk_score INTEGER DEFAULT 0,
        created_at TEXT,
        FOREIGN KEY (bank_id) REFERENCES banks(id)
    )
    ''')
    
    # جدول المعاملات
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        amount REAL,
        location TEXT,
        device_type TEXT,
        transaction_time TEXT,
        risk_score INTEGER,
        status TEXT,
        alert_sent INTEGER DEFAULT 0,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    ''')
    
    # جدول التنبيهات
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id INTEGER,
        customer_id INTEGER,
        alert_type TEXT,
        message TEXT,
        timestamp TEXT,
        resolved INTEGER DEFAULT 0,
        FOREIGN KEY (transaction_id) REFERENCES transactions(id),
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    ''')
    
    # جدول الاحتيالات المسجلة
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fraud_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT UNIQUE,
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
    print("✅ Database initialized successfully")

def add_fraud_case(case_id, amount, description, perpetrators, banks_involved, date, status):
    """إضافة قضية احتيال جديدة"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO fraud_cases (case_id, amount, description, perpetrators, banks_involved, date, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (case_id, amount, description, perpetrators, banks_involved, date, status))
    conn.commit()
    conn.close()

def get_fraud_cases():
    """جلب جميع قضايا الاحتيال"""
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query("SELECT * FROM fraud_cases ORDER BY date DESC", conn)
    conn.close()
    return df

def add_transaction(customer_id, amount, location, device_type, transaction_time, risk_score, status):
    """إضافة معاملة جديدة"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO transactions (customer_id, amount, location, device_type, transaction_time, risk_score, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (customer_id, amount, location, device_type, transaction_time, risk_score, status))
    transaction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return transaction_id

def get_transactions(limit=100):
    """جلب آخر المعاملات"""
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query(f"SELECT * FROM transactions ORDER BY transaction_time DESC LIMIT {limit}", conn)
    conn.close()
    return df

def add_alert(transaction_id, customer_id, alert_type, message):
    """إضافة تنبيه"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO alerts (transaction_id, customer_id, alert_type, message, timestamp)
    VALUES (?, ?, ?, ?, ?)
    ''', (transaction_id, customer_id, alert_type, message, datetime.now().isoformat()))
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
    """تحديد تنبيه كمحلول"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE alerts SET resolved = 1 WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()

def get_stats():
    """جلب الإحصائيات"""
    conn = sqlite3.connect(DATABASE_PATH)
    
    total_transactions = pd.read_sql_query("SELECT COUNT(*) as count FROM transactions", conn).iloc[0]['count']
    high_risk = pd.read_sql_query("SELECT COUNT(*) as count FROM transactions WHERE risk_score > 70", conn).iloc[0]['count']
    alerts_count = pd.read_sql_query("SELECT COUNT(*) as count FROM alerts WHERE resolved = 0", conn).iloc[0]['count']
    fraud_cases_count = pd.read_sql_query("SELECT COUNT(*) as count FROM fraud_cases", conn).iloc[0]['count']
    
    conn.close()
    
    return {
        "total_transactions": total_transactions,
        "high_risk": high_risk,
        "alerts": alerts_count,
        "fraud_cases": fraud_cases_count
    }

def add_sample_data():
    """إضافة بيانات تجريبية"""
    # إضافة قضية Equity
    add_fraud_case(
        case_id="FRAUD-2026-001",
        amount=12600000000,
        description="احتيال إلكتروني عبر الحدود استهدف Equity Bank Kigali",
        perpetrators="سليمان موغيشا، إينوك مباغا كازيغي، بينيديكتو كاتيراغا، فاروق كييمبا، جيرارد أوكيتش، كاتامبا إسما",
        banks_involved="Equity Bank (Kigali), Equity Bank (Uganda)",
        date="2026-02-15",
        status="under_investigation"
    )
    
    # إضافة معاملات تجريبية
    sample_transactions = [
        (1, 5000000, "Kampala", "معروف", "2026-03-24 10:00:00", 15, "approved"),
        (1, 15000000, "Kigali", "جديد", "2026-03-24 23:00:00", 85, "flagged"),
        (1, 2000000, "Kampala", "معروف", "2026-03-23 14:30:00", 10, "approved"),
        (1, 47000000, "Kampala", "معروف", "2026-03-22 09:00:00", 20, "approved"),
        (1, 8000000, "Nairobi", "جديد", "2026-03-24 02:00:00", 75, "flagged"),
    ]
    
    for t in sample_transactions:
        add_transaction(*t)
    
    print("✅ Sample data added")

if __name__ == "__main__":
    init_database()
    add_sample_data()
