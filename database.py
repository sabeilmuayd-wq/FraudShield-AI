import sqlite3
import pandas as pd
import os
from datetime import datetime

DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DATABASE_PATH = os.path.join(DATA_DIR, "fraudshield.db")

def init_database():
    """إنشاء قاعدة البيانات المتطورة"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # 1. جدول البنوك
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS banks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        tier TEXT,
        license_date TEXT,
        status TEXT DEFAULT 'active',
        liquidity REAL DEFAULT 0,
        last_liquidity_check TEXT
    )
    ''')
    
    # 2. جدول العملاء
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
        fraud_alert_count INTEGER DEFAULT 0,
        account_frozen INTEGER DEFAULT 0,
        freeze_date TEXT,
        freeze_reason TEXT,
        created_at TEXT,
        FOREIGN KEY (bank_id) REFERENCES banks(id)
    )
    ''')
    
    # 3. جدول المعاملات (مع دعم Offline)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        amount REAL,
        location TEXT,
        device_type TEXT,
        device_id TEXT,
        transaction_time TEXT,
        risk_score INTEGER,
        status TEXT,
        offline_mode INTEGER DEFAULT 0,
        synced INTEGER DEFAULT 1,
        alert_sent INTEGER DEFAULT 0,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    ''')
    
    # 4. جدول التنبيهات
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id INTEGER,
        customer_id INTEGER,
        alert_type TEXT,
        severity TEXT,
        message TEXT,
        timestamp TEXT,
        resolved INTEGER DEFAULT 0,
        resolution_notes TEXT,
        FOREIGN KEY (transaction_id) REFERENCES transactions(id)
    )
    ''')
    
    # 5. جدول البلاغات المشبوهة (لقضية DFCU)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS suspicious_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        report_date TEXT,
        reported_to_fia INTEGER DEFAULT 0,
        fia_report_date TEXT,
        freeze_start_date TEXT,
        freeze_end_date TEXT,
        status TEXT,
        notes TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    ''')
    
    # 6. جدول قضايا الاحتيال الكبرى
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fraud_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT UNIQUE,
        amount REAL,
        description TEXT,
        perpetrators TEXT,
        banks_involved TEXT,
        countries_involved TEXT,
        detection_date TEXT,
        status TEXT,
        recovery_amount REAL DEFAULT 0
    )
    ''')
    
    # 7. جدول مراقبة السيولة
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS liquidity_monitoring (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bank_id INTEGER,
        branch TEXT,
        cash_reserve REAL,
        date TEXT,
        alert_sent INTEGER DEFAULT 0,
        FOREIGN KEY (bank_id) REFERENCES banks(id)
    )
    ''')
    
    # 8. جدول إجراءات الموارد البشرية (لقضية UGAFODE)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hr_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_name TEXT,
        employee_position TEXT,
        bank_id INTEGER,
        action_type TEXT,
        action_date TEXT,
        reason TEXT,
        documented INTEGER DEFAULT 0,
        legal_review INTEGER DEFAULT 0,
        compensation_paid REAL DEFAULT 0,
        FOREIGN KEY (bank_id) REFERENCES banks(id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Advanced database initialized")

def add_fraud_case(case_id, amount, description, perpetrators, banks_involved, countries_involved, detection_date, status):
    """إضافة قضية احتيال"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO fraud_cases (case_id, amount, description, perpetrators, banks_involved, countries_involved, detection_date, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (case_id, amount, description, perpetrators, banks_involved, countries_involved, detection_date, status))
    conn.commit()
    conn.close()

def get_fraud_cases():
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query("SELECT * FROM fraud_cases ORDER BY detection_date DESC", conn)
    conn.close()
    return df

def add_transaction(customer_id, amount, location, device_type, device_id, transaction_time, risk_score, status, offline_mode=0):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO transactions (customer_id, amount, location, device_type, device_id, transaction_time, risk_score, status, offline_mode)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (customer_id, amount, location, device_type, device_id, transaction_time, risk_score, status, offline_mode))
    transaction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return transaction_id

def add_alert(transaction_id, customer_id, alert_type, severity, message):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO alerts (transaction_id, customer_id, alert_type, severity, message, timestamp)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (transaction_id, customer_id, alert_type, severity, message, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_alerts(unresolved_only=True):
    conn = sqlite3.connect(DATABASE_PATH)
    query = "SELECT * FROM alerts"
    if unresolved_only:
        query += " WHERE resolved = 0"
    query += " ORDER BY timestamp DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def resolve_alert(alert_id, notes=""):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE alerts SET resolved = 1, resolution_notes = ? WHERE id = ?", (notes, alert_id))
    conn.commit()
    conn.close()

def add_suspicious_report(customer_id, report_date, reported_to_fia, freeze_start_date, freeze_end_date, status, notes=""):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO suspicious_reports (customer_id, report_date, reported_to_fia, freeze_start_date, freeze_end_date, status, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (customer_id, report_date, reported_to_fia, freeze_start_date, freeze_end_date, status, notes))
    conn.commit()
    conn.close()

def get_suspicious_reports():
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query("SELECT * FROM suspicious_reports ORDER BY report_date DESC", conn)
    conn.close()
    return df

def update_liquidity(bank_id, branch, cash_reserve):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO liquidity_monitoring (bank_id, branch, cash_reserve, date, alert_sent)
    VALUES (?, ?, ?, ?, 0)
    ''', (bank_id, branch, cash_reserve, datetime.now().isoformat()))
    
    # التحقق من سيولة منخفضة
    if cash_reserve < 100000000:  # أقل من 100 مليون شلن
        cursor.execute("UPDATE liquidity_monitoring SET alert_sent = 1 WHERE id = last_insert_rowid()")
    
    conn.commit()
    conn.close()

def add_hr_action(employee_name, employee_position, bank_id, action_type, action_date, reason, documented=1, legal_review=0):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO hr_actions (employee_name, employee_position, bank_id, action_type, action_date, reason, documented, legal_review)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (employee_name, employee_position, bank_id, action_type, action_date, reason, documented, legal_review))
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DATABASE_PATH)
    
    total_transactions = pd.read_sql_query("SELECT COUNT(*) as count FROM transactions", conn).iloc[0]['count']
    high_risk = pd.read_sql_query("SELECT COUNT(*) as count FROM transactions WHERE risk_score > 70", conn).iloc[0]['count']
    alerts_count = pd.read_sql_query("SELECT COUNT(*) as count FROM alerts WHERE resolved = 0", conn).iloc[0]['count']
    fraud_cases_count = pd.read_sql_query("SELECT COUNT(*) as count FROM fraud_cases", conn).iloc[0]['count']
    frozen_accounts = pd.read_sql_query("SELECT COUNT(*) as count FROM customers WHERE account_frozen = 1", conn).iloc[0]['count']
    
    conn.close()
    
    return {
        "total_transactions": total_transactions,
        "high_risk": high_risk,
        "alerts": alerts_count,
        "fraud_cases": fraud_cases_count,
        "frozen_accounts": frozen_accounts
    }

def add_sample_data():
    """إضافة البيانات الحقيقية من التقارير"""
    
    # قضية Equity Bank Kigali (12.6 مليار)
    add_fraud_case(
        case_id="FRAUD-2026-001",
        amount=12600000000,
        description="احتيال إلكتروني عبر الحدود استهدف Equity Bank Kigali. 6 متهمين أوغنديين تلاعبوا بالبنية التحتية المصرفية.",
        perpetrators="سليمان موغيشا، إينوك مباغا كازيغي، بينيديكتو كاتيراغا، فاروق كييمبا، جيرارد أوكيتش، كاتامبا إسما",
        banks_involved="Equity Bank (Kigali), Equity Bank (Uganda)",
        countries_involved="Uganda, Rwanda",
        detection_date="2026-02-15",
        status="under_investigation"
    )
    
    # قضية DFCU (تجميد حساب 80 مليون لمدة سنتين)
    add_suspicious_report(
        customer_id=1,
        report_date="2024-01-15",
        reported_to_fia=1,
        freeze_start_date="2024-01-20",
        freeze_end_date="2026-03-15",
        status="resolved_court_order",
        notes="المحكمة العليا أمرت بإطلاق الحساب بعد سنتين من التجميد"
    )
    
    print("✅ Sample data added")

if __name__ == "__main__":
    init_database()
    add_sample_data()
