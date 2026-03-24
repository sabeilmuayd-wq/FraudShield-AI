import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
from datetime import datetime

# ==================== إعدادات الصفحة ====================
st.set_page_config(
    page_title="FraudShield AI",
    page_icon="🛡️",
    layout="wide"
)

# ==================== إعداد قاعدة البيانات ====================
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
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id INTEGER,
        message TEXT,
        timestamp TEXT,
        resolved INTEGER DEFAULT 0
    )
    ''')
    
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

def add_transaction(amount, location, device_type, transaction_time, risk_score, status):
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
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO alerts (transaction_id, message, timestamp)
    VALUES (?, ?, ?)
    ''', (transaction_id, message, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_alerts():
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query("SELECT * FROM alerts WHERE resolved = 0 ORDER BY timestamp DESC", conn)
    conn.close()
    return df

def resolve_alert(alert_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE alerts SET resolved = 1 WHERE id = ?", (alert_id,))
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

def add_fraud_case(case_id, amount, description, perpetrators, banks_involved, date, status):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO fraud_cases (case_id, amount, description, perpetrators, banks_involved, date, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (case_id, amount, description, perpetrators, banks_involved, date, status))
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DATABASE_PATH)
    total = pd.read_sql_query("SELECT COUNT(*) as c FROM transactions", conn).iloc[0]['c']
    high_risk = pd.read_sql_query("SELECT COUNT(*) as c FROM transactions WHERE risk_score > 70", conn).iloc[0]['c']
    alerts = pd.read_sql_query("SELECT COUNT(*) as c FROM alerts WHERE resolved = 0", conn).iloc[0]['c']
    fraud_cases = pd.read_sql_query("SELECT COUNT(*) as c FROM fraud_cases", conn).iloc[0]['c']
    conn.close()
    return {"total": total, "high_risk": high_risk, "alerts": alerts, "fraud_cases": fraud_cases}

def add_sample_data():
    """إضافة بيانات تجريبية"""
    # قضية Equity Bank Kigali الحقيقية
    add_fraud_case(
        case_id="FRAUD-2026-001",
        amount=12600000000,
        description="احتيال إلكتروني عبر الحدود استهدف Equity Bank Kigali. 6 متهمين أوغنديين تلاعبوا بالبنية التحتية المصرفية.",
        perpetrators="سليمان موغيشا، إينوك مباغا كازيغي، بينيديكتو كاتيراغا، فاروق كييمبا، جيرارد أوكيتش، كاتامبا إسما",
        banks_involved="Equity Bank (Kigali), Equity Bank (Uganda)",
        date="2026-02-15",
        status="under_investigation"
    )
    
    # قضية العميل (47 مليون اختفت)
    add_fraud_case(
        case_id="FRAUD-2024-001",
        amount=47000000,
        description="47 مليون شلن اختفت من حساب عميل في Equity Bank بعد مكالمة احتيال",
        perpetrators="غير معروفين",
        banks_involved="Equity Bank (Uganda)",
        date="2024-01-15",
        status="investigation"
    )
    
    # معاملات تجريبية
    add_transaction(5000000, "Kampala", "معروف", datetime.now().isoformat(), 15, "approved")
    add_transaction(47000000, "Kampala", "معروف", datetime.now().isoformat(), 20, "approved")
    
    print("✅ Sample data added")

# ==================== كاشف الاحتيال ====================
class FraudDetector:
    def __init__(self):
        self.suspicious_locations = ["Kigali", "Nairobi", "London", "Juba", "Unknown"]
        self.suspicious_devices = ["جديد", "مشبوه", "new", "suspicious"]
        
    def calculate_risk(self, amount, location, device_type, time_of_day):
        risk_score = 0
        alerts = []
        
        # المبلغ
        if amount >= 47000000:
            risk_score += 45
            alerts.append(f"🚨 مبلغ خطر جداً: {amount:,.0f} UGX (مشابه لقضية 47 مليون)")
        elif amount > 10000000:
            risk_score += 30
            alerts.append(f"⚠️ مبلغ كبير: {amount:,.0f} UGX")
        elif amount > 5000000:
            risk_score += 15
            alerts.append(f"⚠️ مبلغ مرتفع: {amount:,.0f} UGX")
        
        # الموقع
        if location in ["Kigali", "Nairobi"]:
            risk_score += 35
            alerts.append(f"🌍 معاملة من {location} – نفس نمط قضية Equity!")
        elif location in self.suspicious_locations:
            risk_score += 25
            alerts.append(f"🌍 معاملة من {location}")
        
        # الجهاز
        if device_type in self.suspicious_devices:
            risk_score += 40
            alerts.append(f"📱 جهاز {device_type}")
        
        # الوقت
        late_hours = ["23:00", "00:00", "01:00", "02:00", "03:00", "04:00"]
        if any(h in time_of_day for h in late_hours):
            risk_score += 20
            alerts.append("🕒 وقت غير معتاد")
        
        risk_score = min(risk_score, 100)
        
        return {
            "risk_score": risk_score,
            "status": "blocked" if risk_score >= 70 else "flagged" if risk_score >= 40 else "approved",
            "alerts": alerts
        }
    
    def get_recommendation(self, risk_score):
        if risk_score >= 70:
            return "🚨 **إجراء فوري:** منع المعاملة، إشعار البنك وهيئة الرقابة"
        elif risk_score >= 40:
            return "⚠️ **إجراء تحقق:** طلب تأكيد من العميل عبر واتساب"
        else:
            return "✅ **معاملة آمنة:** لا يوجد إجراء مطلوب"

# ==================== تهيئة التطبيق ====================
init_database()
detector = FraudDetector()

# التحقق من وجود البيانات
conn = sqlite3.connect(DATABASE_PATH)
count = pd.read_sql_query("SELECT COUNT(*) as c FROM fraud_cases", conn).iloc[0]['c']
conn.close()
if count == 0:
    add_sample_data()

# ==================== تصميم الصفحة ====================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .alert-critical {
        background: #ffebee;
        border-left: 5px solid #e74c3c;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .alert-warning {
        background: #fff3e0;
        border-left: 5px solid #f39c12;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stats-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==================== العنوان ====================
st.markdown("""
<div class='main-header'>
    <h1>🛡️ FraudShield AI</h1>
    <p>نظام كشف الاحتيال المصرفي بالذكاء الاصطناعي</p>
    <p style='font-size: 0.9rem;'>Bank of Uganda | Uganda Bankers Association | Financial Intelligence Authority</p>
</div>
""", unsafe_allow_html=True)

# ==================== الشريط الجانبي ====================
with st.sidebar:
    st.markdown("### 📊 الإحصائيات")
    stats = get_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("إجمالي المعاملات", stats["total"])
        st.metric("تنبيهات نشطة", stats["alerts"])
    with col2:
        st.metric("معاملات عالية الخطورة", stats["high_risk"])
        st.metric("قضايا احتيال", stats["fraud_cases"])
    
    st.markdown("---")
    st.markdown("### 📞 للتواصل")
    st.markdown("""
    **Bank of Uganda**  
    📞 0414-258-441  
    📧 info@bou.or.ug
    
    **Uganda Bankers Association**  
    📞 0312-264-997
    """)

# ==================== التبويبات ====================
tab1, tab2, tab3, tab4 = st.tabs([
    "🛡️ كشف الاحتيال",
    "📋 قضايا الاحتيال",
    "🚨 التنبيهات",
    "📊 التقارير"
])

# ==================== TAB 1 ====================
with tab1:
    st.subheader("🛡️ تحليل معاملة جديدة")
    
    st.info("""
    **🔍 هذا النظام يحلل المعاملات بناءً على عوامل من قضايا حقيقية:**
    - مبلغ 47 مليون+ (مشابه لقضية اختفاء 47 مليون من Equity)
    - معاملات من رواندا/كينيا (مثل قضية 12.6 مليار)
    - أجهزة جديدة/مشبوهة
    - ساعات متأخرة
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        amount = st.number_input("💰 المبلغ (UGX)", min_value=0, step=100000, value=5000000)
        location = st.selectbox("📍 الموقع", ["Kampala", "Kigali", "Nairobi", "Juba", "London", "Unknown"])
        
    with col2:
        device_type = st.selectbox("📱 نوع الجهاز", ["معروف", "جديد", "مشبوه"])
        time_of_day = st.time_input("🕒 وقت المعاملة", datetime.now().time())
        time_str = time_of_day.strftime("%H:%M")
    
    result = detector.calculate_risk(amount, location, device_type, time_str)
    
    st.markdown("---")
    st.markdown("### 🧠 تحليل الذكاء الاصطناعي")
    
    st.progress(result["risk_score"] / 100)
    st.caption(f"**نسبة المخاطرة:** {result['risk_score']}%")
    
    if result["alerts"]:
        for alert in result["alerts"]:
            if result["risk_score"] >= 70:
                st.markdown(f"<div class='alert-critical'>{alert}</div>", unsafe_allow_html=True)
            elif result["risk_score"] >= 40:
                st.markdown(f"<div class='alert-warning'>{alert}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='alert-safe'>{alert}</div>", unsafe_allow_html=True)
    
    st.markdown(f"**📋 التوصية:** {detector.get_recommendation(result['risk_score'])}")
    
    if st.button("✅ تسجيل المعاملة وتحليلها", use_container_width=True):
        transaction_id = add_transaction(
            amount=amount,
            location=location,
            device_type=device_type,
            transaction_time=datetime.now().isoformat(),
            risk_score=result["risk_score"],
            status=result["status"]
        )
        
        if result["risk_score"] >= 40:
            add_alert(transaction_id, ", ".join(result["alerts"]))
        
        st.success(f"✅ تم تسجيل المعاملة رقم: {transaction_id}")
        st.balloons()

# ==================== TAB 2 ====================
with tab2:
    st.subheader("📋 قضايا الاحتيال المسجلة")
    
    fraud_cases = get_fraud_cases()
    
    if not fraud_cases.empty:
        for _, case in fraud_cases.iterrows():
            with st.expander(f"🔴 {case['case_id']} - {case['date']} - {case['amount']:,.0f} UGX"):
                st.markdown(f"""
                **الوصف:** {case['description']}  
                **المتهمون:** {case['perpetrators']}  
                **البنوك المعنية:** {case['banks_involved']}  
                **الحالة:** {case['status']}
                """)
    else:
        st.info("لا توجد قضايا احتيال مسجلة")

# ==================== TAB 3 ====================
with tab3:
    st.subheader("🚨 التنبيهات النشطة")
    
    alerts = get_alerts()
    
    if not alerts.empty:
        for _, alert in alerts.iterrows():
            st.markdown(f"""
            <div class='alert-warning'>
                <strong>⚠️ تنبيه</strong><br>
                المعاملة: {alert['transaction_id']}<br>
                الرسالة: {alert['message']}<br>
                الوقت: {alert['timestamp']}
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"✅ حل التنبيه {alert['id']}", key=f"resolve_{alert['id']}"):
                resolve_alert(alert['id'])
                st.success("تم حل التنبيه")
                st.rerun()
    else:
        st.info("✅ لا توجد تنبيهات نشطة")

# ==================== TAB 4 ====================
with tab4:
    st.subheader("📊 التقارير والتحليلات")
    
    transactions = get_transactions()
    
    if not transactions.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            risk_dist = transactions['risk_score'].value_counts().sort_index()
            fig = px.bar(x=risk_dist.index, y=risk_dist.values, 
                         title="توزيع المعاملات حسب نسبة المخاطرة",
                         labels={'x': 'نسبة المخاطرة', 'y': 'عدد المعاملات'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            location_counts = transactions['location'].value_counts()
            fig = px.pie(values=location_counts.values, names=location_counts.index,
                         title="المعاملات حسب الموقع")
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📋 آخر المعاملات")
        st.dataframe(transactions[['amount', 'location', 'device_type', 'risk_score', 'status']].head(20), use_container_width=True)
        
        csv = transactions.to_csv(index=False)
        st.download_button(
            label="📥 تحميل التقرير (CSV)",
            data=csv,
            file_name=f"fraud_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("لا توجد معاملات مسجلة بعد")
