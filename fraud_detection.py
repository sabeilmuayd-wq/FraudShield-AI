import pandas as pd
import numpy as np
from datetime import datetime

class FraudDetector:
    def __init__(self):
        self.threshold_high = 70
        self.threshold_medium = 40
        
        # المواقع المشبوهة (من قضية Equity)
        self.suspicious_locations = [
            "Kigali", "Nairobi", "London", "Unknown", 
            "Juba", "Dar es Salaam", "Dubai", 
            "New York", "Beijing", "Moscow"
        ]
        
        # الأجهزة المشبوهة
        self.suspicious_devices = ["جديد", "مشبوه", "new", "suspicious", "unknown"]
        
        # العتبات المالية (من تحليل الاحتيالات)
        self.amount_thresholds = {
            "high": 10000000,    # 10 مليون – خطر مرتفع
            "medium": 5000000,   # 5 مليون – خطر متوسط
            "suspicious": 47000000  # 47 مليون – مثل قضية Equity
        }
        
    def calculate_risk(self, amount, location, device_type, device_id, time_of_day, customer_history=None):
        """حساب نسبة المخاطرة المتقدمة"""
        risk_score = 0
        alerts = []
        
        # 1. تحليل المبلغ (مع عتبات دقيقة)
        if amount >= self.amount_thresholds["suspicious"]:
            risk_score += 45
            alerts.append(f"🚨 مبلغ خطر جداً: {amount:,.0f} UGX (مشابه لقضية Equity)")
        elif amount > self.amount_thresholds["high"]:
            risk_score += 30
            alerts.append(f"⚠️ مبلغ كبير جداً: {amount:,.0f} UGX")
        elif amount > self.amount_thresholds["medium"]:
            risk_score += 15
            alerts.append(f"⚠️ مبلغ مرتفع: {amount:,.0f} UGX")
        
        # 2. تحليل الموقع (مع التركيز على رواندا وكينيا – قضية Equity)
        if location in ["Kigali", "Nairobi"]:
            risk_score += 35
            alerts.append(f"🌍 معاملة من {location} – نفس نمط قضية Equity!")
        elif location in self.suspicious_locations:
            risk_score += 25
            alerts.append(f"🌍 معاملة من {location} (خارج أوغندا)")
        
        # 3. تحليل الجهاز
        if device_type in self.suspicious_devices:
            risk_score += 40
            alerts.append(f"📱 جهاز {device_type} (غير معروف – خطر عالي)")
        elif device_type == "جديد":
            risk_score += 25
            alerts.append(f"📱 جهاز جديد غير معروف")
        
        # 4. تحليل الوقت (الساعات المتأخرة)
        late_hours = ["23:00", "00:00", "01:00", "02:00", "03:00", "04:00"]
        if any(h in time_of_day for h in late_hours):
            risk_score += 20
            alerts.append("🕒 وقت غير معتاد (احتمالية احتيال مرتفعة)")
        
        # 5. تحليل تكرار المعاملات (منع الاحتيال المتسلسل)
        if customer_history:
            if customer_history.get("recent_fraud", False):
                risk_score += 40
                alerts.append("⚠️ العميل مرتبط بحادثة احتيال سابقة")
            
            if customer_history.get("high_frequency", False):
                risk_score += 25
                alerts.append("📊 معاملات متكررة غير معتادة")
        
        # 6. تحليل العبر الحدودية (قضية Equity)
        if location in ["Kigali", "Nairobi"] and amount > 5000000:
            risk_score += 15
            alerts.append("🌍⚠️ معاملة عبر الحدود بمبلغ كبير – تنبيه عالي")
        
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
    
    def get_recommendation(self, risk_score, status):
        """توصية متقدمة بناءً على النتائج"""
        if risk_score >= 70:
            return "🚨 **إجراء فوري:** منع المعاملة، إشعار البنك وهيئة الرقابة، إضافة العميل للقائمة السوداء المؤقتة"
        elif risk_score >= 40:
            return "⚠️ **إجراء تحقق:** طلب تأكيد من العميل عبر واتساب/اتصال، تعليق المعاملة 24 ساعة"
        else:
            return "✅ **معاملة آمنة:** لا يوجد إجراء مطلوب"
    
    def get_fraud_pattern_description(self, risk_score, alerts):
        """وصف نمط الاحتيال المحتمل"""
        if risk_score >= 70:
            if any("Kigali" in a or "Nairobi" in a for a in alerts):
                return "🔴 **نمط مشابه لقضية Equity Bank:** معاملة عبر الحدود بمبلغ كبير"
            elif any("مبلغ خطر جداً" in a for a in alerts):
                return "🔴 **مبلغ مشابه لقضية الاحتيال:** 47 مليون شلن أو أكثر"
            else:
                return "🔴 **احتيال محتمل عالي الخطورة:** عدة عوامل خطر متزامنة"
        elif risk_score >= 40:
            return "🟠 **نشاط مشبوه:** يتطلب تحققاً إضافياً"
        else:
            return "🟢 **نشاط طبيعي:** لا يوجد مؤشرات احتيال"
