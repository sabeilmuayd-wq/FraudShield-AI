import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid

from database import (
    init_database, get_fraud_cases, get_transactions, 
    get_alerts, resolve_alert, get_stats, add_transaction,
    add_alert, get_suspicious_reports, update_liquidity,
    DATABASE_PATH
)
from fraud_detection import FraudDetector

# تهيئة الصفحة
st.set_page_config(
    page_title="FraudShield AI - نظام كشف الاحتيال المصرفي المتطور",
    page_icon="🛡️",
    layout="wide"
)

# تهيئة
init_database()
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
    .stats-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .case-card {
        background: #f8f9fa;
        border-left: 5px solid #e74c3c;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== العنوان ====================
st.markdown("""
<div class='main-header'>
    <h1>🛡️ FraudShield AI</h1>
    <p>نظام كشف الاحتيال المصرفي وإدارة المخاطر المتكامل</p>
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
    st.metric("حسابات مجمدة", stats["frozen_accounts"])
    
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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛡️ كشف الاحتيال",
    "📋 قضايا الاحتيال",
    "🚨 التنبيهات",
    "📊 التقارير",
    "⚖️ الامتثال المصرفي"
])

# ==================== TAB 1: كشف الاحتيال المتقدم ====================
with tab1:
    st.subheader("🛡️ تحليل معاملة جديدة (نظام كشف متقدم)")
    
    st.info("""
    **🔍 هذا النظام يحلل المعاملات بناءً على 6 عوامل:**
    1. المبلغ (مع عتبات من قضية Equity: 47 مليون+ خطر جداً)
    2. الموقع (تركيز خاص على رواندا وكينيا – مصدر قضية الاحتيال)
    3. الجهاز (أجهزة جديدة/مشبوهة)
    4. الوقت (الساعات المتأخرة)
    5. النمط السلوكي (معاملات متكررة)
    6. العبر الحدودية (نفس نمط قضية Equity)
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        amount = st.number_input("💰 المبلغ (UGX)", min_value=0, step=100000, value=5000000)
        location = st.selectbox("📍 الموقع", ["Kampala", "Kigali", "Nairobi", "Juba", "London", "Unknown"])
        
    with col2:
        device_type = st.selectbox("📱 نوع الجهاز", ["معروف", "جديد", "مشبوه"])
        device_id = st.text_input("🆔 معرف الجهاز (اختياري)", value=str(uuid.uuid4())[:8])
        time_of_day = st.time_input("🕒 وقت المعاملة", datetime.now().time())
        time_str = time_of_day.strftime("%H:%M")
    
    # تحليل المخاطرة
    result = detector.calculate_risk(amount, location, device_type, device_id, time_str)
    
    st.markdown("---")
    st.markdown("### 🧠 تحليل الذكاء الاصطناعي")
    
    # عرض نسبة المخاطرة
    st.progress(result["risk_score"] / 100)
    st.caption(f"نسبة المخاطرة: {result['risk_score']}%")
    
    # عرض نمط الاحتيال
    pattern = detector.get_fraud_pattern_description(result["risk_score"], result["alerts"])
    st.markdown(f"**📊 نمط التحليل:** {pattern}")
    
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
    st.markdown(f"**📋 التوصية:** {detector.get_recommendation(result['risk_score'], result['status'])}")
    
    # زر تسجيل المعاملة
    if st.button("✅ تسجيل المعاملة وتحليلها", use_container_width=True):
        transaction_id = add_transaction(
            customer_id=1,
            amount=amount,
            location=location,
            device_type=device_type,
            device_id=device_id,
            transaction_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            risk_score=result["risk_score"],
            status=result["status"],
            offline_mode=0
        )
        
        if result["risk_score"] >= 40:
            add_alert(
                transaction_id=transaction_id,
                customer_id=1,
                alert_type=result["alert_level"],
                severity="high" if result["risk_score"] >= 70 else "medium",
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
            with st.expander(f"🔴 {case['case_id']} - {case['detection_date']} - {case['amount']:,.0f} UGX"):
                st.markdown(f"""
                **الوصف:** {case['description']}  
                **المتهمون:** {case['perpetrators']}  
                **البنوك المعنية:** {case['banks_involved']}  
                **الدول المعنية:** {case['countries_involved']}  
                **الحالة:** {case['status']}
                """)
    else:
        st.info("لا توجد قضايا احتيال مسجلة")

# ==================== TAB 3: التنبيهات ====================
with tab3:
    st.subheader("🚨 التنبيهات النشطة")
    
    alerts = get_alerts(unresolved_only=True)
    
    if not alerts.empty:
        for _, alert in alerts.iterrows():
            severity_color = "alert-critical" if alert['severity'] == "high" else "alert-warning"
            st.markdown(f"""
            <div class='{severity_color}'>
                <strong>{'⚠️ تنبيه عالي الخطورة' if alert['severity'] == 'high' else '⚠️ تنبيه متوسط الخطورة'}</strong><br>
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
            risk_dist = transactions['risk_score'].value_counts().sort_index()
            fig = px.bar(x=risk_dist.index, y=risk_dist.values, 
                         title="توزيع المعاملات حسب نسبة المخاطرة")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            location_counts = transactions['location'].value_counts()
            fig = px.pie(values=location_counts.values, names=location_counts.index,
                         title="المعاملات حسب الموقع")
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📋 آخر المعاملات")
        st.dataframe(transactions[['amount', 'location', 'device_type', 'risk_score', 'status']].head(20), use_container_width=True)
        
        csv = transactions.to_csv(index=False)
        st.download_button("📥 تحميل التقرير", csv, f"fraud_report_{datetime.now().strftime('%Y%m%d')}.csv")
    else:
        st.info("لا توجد معاملات مسجلة بعد")

# ==================== TAB 5: الامتثال المصرفي ====================
with tab5:
    st.subheader("⚖️ نظام الامتثال المصرفي")
    
    st.markdown("""
    ### 📋 بلاغات مشبوهة وحسابات مجمدة
    """)
    
    reports = get_suspicious_reports()
    
    if not reports.empty:
        for _, report in reports.iterrows():
            st.markdown(f"""
            <div class='case-card'>
                <strong>📅 تاريخ البلاغ:</strong> {report['report_date']}<br>
                <strong>🏦 تم الإبلاغ لهيئة الاستخبارات المالية:</strong> {'✅ نعم' if report['reported_to_fia'] else '❌ لا'}<br>
                <strong>🔒 تاريخ التجميد:</strong> {report['freeze_start_date']} → {report['freeze_end_date']}<br>
                <strong>📌 الحالة:</strong> {report['status']}<br>
                <strong>📝 ملاحظات:</strong> {report['notes']}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    ### ⚖️ توصيات امتثالية (من قضايا حقيقية)
    
    | القضية | التوصية |
    |--------|---------|
    | **DFCU (تجميد 80 مليون لمدة سنتين)** | يجب أن لا يتجاوز التجميد 30 يوماً دون إبلاغ FIA |
    | **UGAFODE (فصل تعسفي)** | توثيق جميع إجراءات الموارد البشرية، مراجعة قانونية إلزامية |
    | **Equity Bank Kigali (12.6 مليار)** | تفعيل نظام كشف عبر الحدود، مراقبة معاملات رواندا وكينيا |
    | **انقطاع الإنترنت (40% معاملات)** | تفعيل نظام Offline Mode للمدفوعات الأساسية |
    """)
