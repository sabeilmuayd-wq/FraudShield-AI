import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class FraudDetector:
    def __init__(self):
        self.threshold_high = 70
        self.threshold_medium = 40
        
    def calculate_risk(self, amount, location, device_type, time_of_day, customer_history=None):
        """حساب نسبة المخاطرة للمعاملة"""
        risk_score = 0
        alerts = []
        
        # 1. تحليل المبلغ
        if amount > 10000000:
            risk_score += 30
            alerts.append("⚠️ مبلغ كبير غير معتاد")
        elif amount > 5000000:
            risk_score += 15
            alerts.append("⚠️ مبلغ مرتفع")
        
        # 2. تحليل الموقع
        suspicious_locations = ["Kigali", "Nairobi", "London", "Unknown"]
        if location in suspicious_locations:
            risk_score += 25
            alerts.append(f"🌍 معاملة من {location} (خارج أوغندا)")
        
        # 3. تحليل الجهاز
        if device_type == "جهاز جديد":
            risk_score += 25
            alerts.append("📱 جهاز جديد غير معروف")
        elif device_type == "جهاز مشبوه":
            risk_score += 40
            alerts.append("⚠️ جهاز مشبوه سابقاً")
        
        # 4. تحليل الوقت
        late_hours = ["23:00", "00:00", "01:00", "02:00", "03:00", "04:00"]
        if any(h in time_of_day for h in late_hours):
            risk_score += 20
            alerts.append("🕒 وقت غير معتاد")
        
        # 5. تحليل تاريخ العميل (إن وجد)
        if customer_history:
            if customer_history.get("recent_fraud", False):
                risk_score += 30
                alerts.append("⚠️ العميل مرتبط بحادثة احتيال سابقة")
            
            if customer_history.get("unusual_pattern", False):
                risk_score += 20
                alerts.append("📊 نمط معاملات غير معتاد")
        
        risk_score = min(risk_score, 100)
        
        # تحديد الحالة
        if risk_score >= self.threshold_high:
            status = "blocked"
            alert_level = "critical"
        elif risk_score >= self.threshold_medium:
            status = "flagged"
            alert_level = "warning"
        else:
            status = "approved"
            alert_level = "normal"
        
        return {
            "risk_score": risk_score,
            "status": status,
            "alert_level": alert_level,
            "alerts": alerts
        }
    
    def get_recommendation(self, risk_score):
        """توصية بناءً على نسبة المخاطرة"""
        if risk_score >= 70:
            return "🚨 **إجراء فوري:** منع المعاملة، إشعار البنك وهيئة الرقابة"
        elif risk_score >= 40:
            return "⚠️ **إجراء تحقق:** طلب تأكيد من العميل عبر واتساب/اتصال"
        else:
            return "✅ **معاملة آمنة:** لا يوجد إجراء مطلوب"

# تحليل المعاملات السابقة للكشف عن الأنماط
def analyze_customer_pattern(transactions_df, customer_id):
    """تحليل نمط معاملات العميل"""
    if transactions_df.empty:
        return {"recent_fraud": False, "unusual_pattern": False}
    
    customer_tx = transactions_df[transactions_df['customer_id'] == customer_id]
    
    if len(customer_tx) < 3:
        return {"recent_fraud": False, "unusual_pattern": False}
    
    # حساب متوسط المعاملات
    avg_amount = customer_tx['amount'].mean()
    std_amount = customer_tx['amount'].std()
    
    # التحقق من المعاملات الأخيرة
    recent_tx = customer_tx.tail(5)
    unusual = any(tx['amount'] > avg_amount + 2 * std_amount for _, tx in recent_tx.iterrows())
    
    return {
        "recent_fraud": False,  # سيتم تحديثه من قاعدة بيانات الاحتيالات
        "unusual_pattern": unusual
    }
