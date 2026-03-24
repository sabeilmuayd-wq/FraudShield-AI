import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
from datetime import datetime

# ==================== إعدادات الصفحة ====================
st.set_page_config(
    page_title="FraudShield AI - Banking Security System",
    page_icon="🛡️",
    layout="wide"
)

# ==================== إعداد اللغة ====================
if "language" not in st.session_state:
    st.session_state.language = "en"

# ==================== الترجمة (إنجليزي + سواحلي) ====================
translations = {
    "en": {
        "title": "🛡️ FraudShield AI",
        "subtitle": "Banking Fraud Detection & Compliance System",
        "partners": "Bank of Uganda | Uganda Bankers Association",
        "stats": "📊 Statistics",
        "total_transactions": "Total Transactions",
        "high_risk": "High Risk",
        "active_alerts": "Active Alerts",
        "fraud_cases": "Fraud Cases",
        "contact": "📞 Contact",
        "new_analysis": "🛡️ New Transaction Analysis",
        "amount": "💰 Amount (UGX)",
        "location": "📍 Location",
        "device_type": "📱 Device Type",
        "known": "Known",
        "new": "New",
        "suspicious": "Suspicious",
        "time": "🕒 Transaction Time",
        "analyze": "🧠 AI Analysis",
        "risk_score": "Risk Score",
        "recommendation": "📋 Recommendation",
        "block_immediately": "🚨 **Immediate Action:** Block transaction, notify Bank and FIA",
        "verify_customer": "⚠️ **Verification Required:** Confirm with customer via WhatsApp/call",
        "safe": "✅ **Safe Transaction:** No action required",
        "register": "✅ Register Transaction",
        "registered": "Transaction registered successfully!",
        "fraud_cases_title": "📋 Registered Fraud Cases",
        "case_id": "Case ID",
        "description": "Description",
        "perpetrators": "Perpetrators",
        "banks": "Banks Involved",
        "status": "Status",
        "alerts_title": "🚨 Active Alerts",
        "resolve": "✅ Resolve Alert",
        "reports_title": "📊 Reports & Analytics",
        "transactions_by_risk": "Transactions by Risk Score",
        "transactions_by_location": "Transactions by Location",
        "recent_transactions": "📋 Recent Transactions",
        "download_report": "📥 Download Report (CSV)",
        "amount_alert": "🚨 Extremely high amount: {amount:,} UGX (similar to 47M case)",
        "high_amount": "⚠️ High amount: {amount:,} UGX",
        "medium_amount": "⚠️ Medium amount: {amount:,} UGX",
        "location_alert": "🌍 Transaction from {location} – same pattern as Equity case!",
        "location_warning": "🌍 Transaction from {location}",
        "device_alert": "📱 {device} device",
        "time_alert": "🕒 Unusual transaction time",
        "equity_case": "Equity Bank Kigali Case (12.6 Billion UGX)",
        "customer_case": "Customer Case (47 Million UGX Disappeared)",
        "equity_desc": "Cross-border electronic fraud targeting Equity Bank Kigali. 6 Ugandan suspects manipulated banking infrastructure.",
        "customer_desc": "47 million UGX disappeared from customer account after a fraudulent phone call."
    },
    "sw": {
        "title": "🛡️ FraudShield AI",
        "subtitle": "Mfumo wa Kugundua Ulaghai wa Benki",
        "partners": "Benki Kuu ya Uganda | Chama cha Benki Uganda",
        "stats": "📊 Takwimu",
        "total_transactions": "Jumla ya Miamala",
        "high_risk": "Hatari Kubwa",
        "active_alerts": "Arifa Hai",
        "fraud_cases": "Kesi za Ulaghai",
        "contact": "📞 Wasiliana",
        "new_analysis": "🛡️ Uchambuzi wa Miamala Mpya",
        "amount": "💰 Kiasi (UGX)",
        "location": "📍 Mahali",
        "device_type": "📱 Aina ya Kifaa",
        "known": "Inayojulikana",
        "new": "Mpya",
        "suspicious": "Inayotiliwa shaka",
        "time": "🕒 Muda wa Muamala",
        "analyze": "🧠 Uchambuzi wa AI",
        "risk_score": "Kiwango cha Hatari",
        "recommendation": "📋 Ushauri",
        "block_immediately": "🚨 **Hatua ya Haraka:** Zuia muamala, arifu benki na FIA",
        "verify_customer": "⚠️ **Uthibitishaji Unahitajika:** Thibitisha na mteja kwa WhatsApp/simu",
        "safe": "✅ **Muamala Salama:** Hakuna hatua inayohitajika",
        "register": "✅ Rekodi Muamala",
        "registered": "Muamala umerekodiwa kikamilifu!",
        "fraud_cases_title": "📋 Kesi za Ulaghai Zilizorekodiwa",
        "case_id": "Namba ya Kesi",
        "description": "Maelezo",
        "perpetrators": "Washukiwa",
        "banks": "Benki Zinazohusika",
        "status": "Hali",
        "alerts_title": "🚨 Arifa Hai",
        "resolve": "✅ Tatua Arifa",
        "reports_title": "📊 Ripoti na Uchambuzi",
        "transactions_by_risk": "Miamala kwa Kiwango cha Hatari",
        "transactions_by_location": "Miamala kwa Mahali",
        "recent_transactions": "📋 Miamala ya Hivi Karibuni",
        "download_report": "📥 Pakua Ripoti (CSV)",
        "amount_alert": "🚨 Kiasi kikubwa sana: {amount:,} UGX (kama kesi ya Milioni 47)",
        "high_amount": "⚠️ Kiasi kikubwa: {amount:,} UGX",
        "medium_amount": "⚠️ Kiasi cha wastani: {amount:,} UGX",
        "location_alert": "🌍 Muamala kutoka {location} – sawa na kesi ya Equity!",
        "location_warning": "🌍 Muamala kutoka {location}",
        "device_alert": "📱 Kifaa {device}",
        "time_alert": "🕒 Muda usio wa kawaida",
        "equity_case": "Kesi ya Benki ya Equity Kigali (Bilioni 12.6 UGX)",
        "customer_case": "Kesi ya Mteja (Milioni 47 UGX Zilipotea)",
        "equity_desc": "Ulaghai wa kielektroniki wa kuvuka mpaka uliolenga Benki ya Equity Kigali. Washukiwa 6 wa Uganda walidanganya mfumo wa benki.",
        "customer_desc": "Milioni 47 UGX zilipotea kutoka akaunti ya mteja baada ya simu ya ulaghai."
    }
}

def t(key):
    return translations[st.session_state.language].get(key, key)

# ==================== قاعدة البيانات ====================
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DATABASE_PATH = os.path.join(DATA_DIR, "fraudshield.db")

def init_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL,
        location TEXT,
        device_type TEXT,
        transaction_time TEXT,
        risk_score INTEGER,
        status TEXT
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id INTEGER,
        message TEXT,
        timestamp TEXT,
        resolved INTEGER DEFAULT 0
    )''')
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
    )''')
    conn.commit()
    conn.close()

def add_transaction(amount, location, device_type, transaction_time, risk_score, status):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO transactions (amount, location, device_type, transaction_time, risk_score, status)
    VALUES (?, ?, ?, ?, ?, ?)''', (amount, location, device_type, transaction_time, risk_score, status))
    tid = cursor.lastrowid
    conn.commit()
    conn.close()
    return tid

def add_alert(tid, message):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO alerts (transaction_id, message, timestamp)
    VALUES (?, ?, ?)''', (tid, message, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_alerts():
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query("SELECT * FROM alerts WHERE resolved = 0 ORDER BY timestamp DESC", conn)
    conn.close()
    return df

def resolve_alert(aid):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE alerts SET resolved = 1 WHERE id = ?", (aid,))
    conn.commit()
    conn.close()

def get_transactions():
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query("SELECT * FROM transactions ORDER BY id DESC LIMIT 100", conn)
    conn.close()
    return df

def get_fraud_cases():
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query("SELECT * FROM fraud_cases ORDER BY date DESC", conn)
    conn.close()
    return df

def add_fraud_case(cid, amount, desc, perps, banks, date, status):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO fraud_cases (case_id, amount, description, perpetrators, banks_involved, date, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)''', (cid, amount, desc, perps, banks, date, status))
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DATABASE_PATH)
    total = pd.read_sql_query("SELECT COUNT(*) as c FROM transactions", conn).iloc[0]['c']
    high = pd.read_sql_query("SELECT COUNT(*) as c FROM transactions WHERE risk_score > 70", conn).iloc[0]['c']
    alerts = pd.read_sql_query("SELECT COUNT(*) as c FROM alerts WHERE resolved = 0", conn).iloc[0]['c']
    cases = pd.read_sql_query("SELECT COUNT(*) as c FROM fraud_cases", conn).iloc[0]['c']
    conn.close()
    return {"total": total, "high": high, "alerts": alerts, "cases": cases}

def add_sample_data():
    add_fraud_case(
        "FRAUD-2026-001", 12600000000,
        t("equity_desc"),
        "Suleiman Mugisha, Enock Mbaga Kazige, Benedicto Kateraga, Farouk Kyimba, Gerald Oketch, Katamba Isma",
        "Equity Bank (Kigali), Equity Bank (Uganda)",
        "2026-02-15", "under_investigation"
    )
    add_fraud_case(
        "FRAUD-2024-001", 47000000,
        t("customer_desc"),
        "Unknown",
        "Equity Bank (Uganda)",
        "2024-01-15", "investigation"
    )
    add_transaction(5000000, "Kampala", "Known", datetime.now().isoformat(), 15, "approved")
    add_transaction(47000000, "Kampala", "Known", datetime.now().isoformat(), 20, "approved")

# ==================== كاشف الاحتيال ====================
class FraudDetector:
    def __init__(self):
        self.suspicious_locations = ["Kigali", "Nairobi", "London", "Juba", "Unknown"]
        self.suspicious_devices = ["New", "Suspicious", "جديد", "مشبوه"]
        
    def calculate_risk(self, amount, location, device_type, time_str):
        risk = 0
        alerts = []
        
        if amount >= 47000000:
            risk += 45
            alerts.append(t("amount_alert").format(amount=amount))
        elif amount > 10000000:
            risk += 30
            alerts.append(t("high_amount").format(amount=amount))
        elif amount > 5000000:
            risk += 15
            alerts.append(t("medium_amount").format(amount=amount))
        
        if location in ["Kigali", "Nairobi"]:
            risk += 35
            alerts.append(t("location_alert").format(location=location))
        elif location in self.suspicious_locations:
            risk += 25
            alerts.append(t("location_warning").format(location=location))
        
        if device_type in self.suspicious_devices:
            risk += 40
            alerts.append(t("device_alert").format(device=device_type))
        
        late = ["23:00", "00:00", "01:00", "02:00", "03:00", "04:00"]
        if any(h in time_str for h in late):
            risk += 20
            alerts.append(t("time_alert"))
        
        risk = min(risk, 100)
        status = "blocked" if risk >= 70 else "flagged" if risk >= 40 else "approved"
        
        return {"risk": risk, "status": status, "alerts": alerts}
    
    def get_recommendation(self, risk):
        if risk >= 70:
            return t("block_immediately")
        elif risk >= 40:
            return t("verify_customer")
        return t("safe")

# ==================== تهيئة التطبيق ====================
init_database()
detector = FraudDetector()

conn = sqlite3.connect(DATABASE_PATH)
count = pd.read_sql_query("SELECT COUNT(*) as c FROM fraud_cases", conn).iloc[0]['c']
conn.close()
if count == 0:
    add_sample_data()

# ==================== واجهة التطبيق ====================
st.markdown("""
<style>
    .main-header { text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); border-radius: 15px; margin-bottom: 2rem; color: white; }
    .alert-critical { background: #ffebee; border-left: 5px solid #e74c3c; padding: 1rem; border-radius: 10px; margin: 1rem 0; }
    .alert-warning { background: #fff3e0; border-left: 5px solid #f39c12; padding: 1rem; border-radius: 10px; margin: 1rem 0; }
    .stats-card { background: white; padding: 1rem; border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# ==================== أزرار اللغة ====================
col1, col2 = st.columns(2)
with col1:
    if st.button("🇬🇧 English", use_container_width=True):
        st.session_state.language = "en"
        st.rerun()
with col2:
    if st.button("🇺🇬 Kiswahili", use_container_width=True):
        st.session_state.language = "sw"
        st.rerun()

# ==================== العنوان ====================
st.markdown(f"""
<div class='main-header'>
    <h1>{t('title')}</h1>
    <p>{t('subtitle')}</p>
    <p style='font-size: 0.9rem;'>{t('partners')}</p>
</div>
""", unsafe_allow_html=True)

# ==================== الشريط الجانبي ====================
with st.sidebar:
    st.markdown(f"### {t('stats')}")
    stats = get_stats()
    st.metric(t("total_transactions"), stats["total"])
    st.metric(t("high_risk"), stats["high"])
    st.metric(t("active_alerts"), stats["alerts"])
    st.metric(t("fraud_cases"), stats["cases"])
    st.markdown("---")
    st.markdown(f"### {t('contact')}")
    st.markdown("**Bank of Uganda**  \n📞 0414-258-441  \n📧 info@bou.or.ug")
    st.markdown("**Uganda Bankers Association**  \n📞 0312-264-997")

# ==================== التبويبات ====================
tabs = st.tabs([t("new_analysis"), t("fraud_cases_title"), t("alerts_title"), t("reports_title")])

# ==================== TAB 1 ====================
with tabs[0]:
    st.subheader(t("new_analysis"))
    
    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input(t("amount"), min_value=0, step=100000, value=5000000)
        location = st.selectbox(t("location"), ["Kampala", "Kigali", "Nairobi", "Juba", "London", "Unknown"])
    with col2:
        device_type = st.selectbox(t("device_type"), [t("known"), t("new"), t("suspicious")])
        time_input = st.time_input(t("time"), datetime.now().time())
        time_str = time_input.strftime("%H:%M")
    
    result = detector.calculate_risk(amount, location, device_type, time_str)
    
    st.markdown("---")
    st.markdown(f"### {t('analyze')}")
    st.progress(result["risk"] / 100)
    st.caption(f"**{t('risk_score')}:** {result['risk']}%")
    
    for alert in result["alerts"]:
        if result["risk"] >= 70:
            st.markdown(f"<div class='alert-critical'>{alert}</div>", unsafe_allow_html=True)
        elif result["risk"] >= 40:
            st.markdown(f"<div class='alert-warning'>{alert}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='alert-safe'>{alert}</div>", unsafe_allow_html=True)
    
    st.markdown(f"**{t('recommendation')}** {detector.get_recommendation(result['risk'])}")
    
    if st.button(t("register"), use_container_width=True):
        tid = add_transaction(amount, location, device_type, datetime.now().isoformat(), result["risk"], result["status"])
        if result["risk"] >= 40:
            add_alert(tid, ", ".join(result["alerts"]))
        st.success(f"✅ {t('registered')}")
        st.balloons()

# ==================== TAB 2 ====================
with tabs[1]:
    st.subheader(t("fraud_cases_title"))
    cases = get_fraud_cases()
    if not cases.empty:
        for _, c in cases.iterrows():
            with st.expander(f"🔴 {c['case_id']} - {c['date']} - {c['amount']:,.0f} UGX"):
                st.write(f"**{t('description')}:** {c['description']}")
                st.write(f"**{t('perpetrators')}:** {c['perpetrators']}")
                st.write(f"**{t('banks')}:** {c['banks_involved']}")
                st.write(f"**{t('status')}:** {c['status']}")
    else:
        st.info("No cases")

# ==================== TAB 3 ====================
with tabs[2]:
    st.subheader(t("alerts_title"))
    alerts = get_alerts()
    if not alerts.empty:
        for _, a in alerts.iterrows():
            st.markdown(f"<div class='alert-warning'><strong>⚠️ Alert</strong><br>{a['message']}<br>🕒 {a['timestamp']}</div>", unsafe_allow_html=True)
            if st.button(f"{t('resolve')} {a['id']}", key=f"res_{a['id']}"):
                resolve_alert(a['id'])
                st.rerun()
    else:
        st.info("✅ No active alerts")

# ==================== TAB 4 ====================
with tabs[3]:
    st.subheader(t("reports_title"))
    txns = get_transactions()
    if not txns.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(x=txns['risk_score'].value_counts().index, y=txns['risk_score'].value_counts().values, title=t("transactions_by_risk"))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.pie(values=txns['location'].value_counts().values, names=txns['location'].value_counts().index, title=t("transactions_by_location"))
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(txns[['amount', 'location', 'device_type', 'risk_score', 'status']].head(20), use_container_width=True)
        csv = txns.to_csv(index=False)
        st.download_button(t("download_report"), csv, f"fraud_report_{datetime.now().strftime('%Y%m%d')}.csv")
    else:
        st.info("No transactions")
