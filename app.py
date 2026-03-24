import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sqlite3

from database import (
    init_database, get_fraud_cases, get_transactions, 
    get_alerts, resolve_alert, get_stats, add_transaction,
    add_alert, DATABASE_PATH
)
from fraud_detection import FraudDetector, analyze_customer_pattern

# ==================== تهيئة الصفحة ====================
st.set_page_config(
    page_title="FraudShield AI - نظام كشف الاحتيال المصرفي",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تهيئة قاعدة البيانات
init_database()

# إنشاء كاشف الاحتيال
detector = FraudDetector()

# ==================== التصميم ====================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
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
    .alert-safe {
        background: #e8f5e9;
        border-left: 5px solid #2ecc71;
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
    
    st.metric("إجمالي المعاملات", stats["total_transactions"])
    st.metric("معاملات عالية المخاطرة", stats["high_risk"])
    st.metric("تنبيهات نشطة", stats["alerts"])
    st.metric("قضايا احتيال مسجلة", stats["fraud_cases"])
    
    st.markdown("---")
    st.markdown("### 📞 للتواصل")
    st.markdown("""
    **Bank of Uganda**  
    📞 0414-258-441  
    📧 info@bou.or.ug
    
    **Uganda Bankers Association**  
    📞 0312-264-997  
    📧 info@ubauganda.com
    
    **Financial Intelligence Authority**  
    📞 0392-001-666
    """)

# ==================== التبويبات ====================
tab1, tab2, tab3, tab4 = st.tabs([
    "🛡️ كشف الاحتيال",
    "📋 قضايا الاحتيال",
    "🚨 التنبيهات",
    "📊 التقارير"
])

# ==================== TAB 1: كشف الاحتيال ====================
with tab1:
    st.subheader("🛡️ تحليل معاملة جديدة")
    
    col1, col2 = st.columns(2)
    
    with col1:
        amount = st.number_input("💰 المبلغ (UGX)", min_value=0, step=100000, value=5000000)
        location = st.selectbox("📍 الموقع", ["Kampala", "Kigali", "Nairobi", "London", "Juba", "Unknown"])
        
    with col2:
        device_type = st.selectbox("📱 نوع الجهاز", ["معروف", "جديد", "مشبوه"])
        time_of_day = st.time_input("🕒 وقت المعاملة", datetime.now().time())
        time_str = time_of_day.strftime("%H:%M")
    
    # تحليل المخاطرة
    result = detector.calculate_risk(amount, location, device_type, time_str)
    
    st.markdown("---")
    st.markdown("### 🧠 تحليل الذكاء الاصطناعي")
    
    # عرض نسبة المخاطرة
    st.progress(result["risk_score"] / 100)
    st.caption(f"نسبة المخاطرة: {result['risk_score']}%")
    
    # عرض التنبيهات
    if result["alerts"]:
        for alert in result["alerts"]:
            if result["risk_score"] >= 70:
                st.markdown(f"<div class='alert-critical'>{alert}</div>", unsafe_allow_html=True)
            elif result["risk_score"] >= 40:
                st.markdown(f"<div class='alert-warning'>{alert}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='alert-safe'>{alert}</div>", unsafe_allow_html=True)
    
    # التوصية
    st.markdown(f"**📋 التوصية:** {detector.get_recommendation(result['risk_score'])}")
    
    # زر تسجيل المعاملة
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ تسجيل المعاملة وتحليلها", use_container_width=True):
            # تسجيل المعاملة في قاعدة البيانات
            transaction_id = add_transaction(
                customer_id=1,  # مؤقت
                amount=amount,
                location=location,
                device_type=device_type,
                transaction_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                risk_score=result["risk_score"],
                status=result["status"]
            )
            
            # إضافة تنبيه إذا لزم الأمر
            if result["risk_score"] >= 40:
                add_alert(
                    transaction_id=transaction_id,
                    customer_id=1,
                    alert_type=result["alert_level"],
                    message=", ".join(result["alerts"])
                )
            
            st.success(f"✅ تم تسجيل المعاملة رقم: {transaction_id}")
            st.balloons()

# ==================== TAB 2: قضايا الاحتيال ====================
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
        st.info("لا توجد قضايا احتيال مسجلة بعد")
    
    st.markdown("---")
    st.markdown("### ➕ إضافة قضية احتيال جديدة")
    
    col1, col2 = st.columns(2)
    with col1:
        new_case_id = st.text_input("رقم القضية", placeholder="FRAUD-2026-XXX")
        new_amount = st.number_input("المبلغ (UGX)", min_value=0, step=1000000)
        new_date = st.date_input("التاريخ")
    with col2:
        new_perpetrators = st.text_input("المتهمون")
        new_banks = st.text_input("البنوك المعنية")
        new_status = st.selectbox("الحالة", ["under_investigation", "court", "closed"])
    
    new_description = st.text_area("وصف القضية")
    
    if st.button("➕ إضافة قضية", use_container_width=True):
        from database import add_fraud_case
        add_fraud_case(
            case_id=new_case_id,
            amount=new_amount,
            description=new_description,
            perpetrators=new_perpetrators,
            banks_involved=new_banks,
            date=new_date.isoformat(),
            status=new_status
        )
        st.success("✅ تم إضافة القضية")
        st.rerun()

# ==================== TAB 3: التنبيهات ====================
with tab3:
    st.subheader("🚨 التنبيهات النشطة")
    
    alerts = get_alerts(unresolved_only=True)
    
    if not alerts.empty:
        for _, alert in alerts.iterrows():
            with st.container():
                if alert['alert_type'] == 'critical':
                    st.markdown(f"""
                    <div class='alert-critical'>
                        <strong>⚠️ تنبيه عالي الخطورة</strong><br>
                        المعاملة: {alert['transaction_id']}<br>
                        الرسالة: {alert['message']}<br>
                        الوقت: {alert['timestamp']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='alert-warning'>
                        <strong>⚠️ تنبيه متوسط الخطورة</strong><br>
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

# ==================== TAB 4: التقارير ====================
with tab4:
    st.subheader("📊 التقارير والتحليلات")
    
    transactions = get_transactions(limit=100)
    
    if not transactions.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # توزيع المخاطر
            risk_dist = transactions['risk_score'].value_counts().sort_index()
            fig = px.bar(x=risk_dist.index, y=risk_dist.values, 
                         title="توزيع المعاملات حسب نسبة المخاطرة",
                         labels={'x': 'نسبة المخاطرة', 'y': 'عدد المعاملات'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # المعاملات حسب الموقع
            location_counts = transactions['location'].value_counts()
            fig = px.pie(values=location_counts.values, names=location_counts.index,
                         title="المعاملات حسب الموقع")
            st.plotly_chart(fig, use_container_width=True)
        
        # آخر المعاملات
        st.subheader("📋 آخر المعاملات")
        st.dataframe(transactions[['amount', 'location', 'device_type', 'risk_score', 'status']].head(20), use_container_width=True)
        
        # تصدير التقرير
        csv = transactions.to_csv(index=False)
        st.download_button(
            label="📥 تحميل التقرير (CSV)",
            data=csv,
            file_name=f"fraudshield_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("لا توجد معاملات مسجلة بعد")
