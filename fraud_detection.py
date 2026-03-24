from datetime import datetime

class FraudDetector:
    def __init__(self):
        self.threshold_high = 70
        self.threshold_medium = 40
        
        # المواقع المشبوهة
        self.suspicious_locations = [
            "Kigali", "Nairobi", "London", "Unknown", 
            "Juba", "Dar es Salaam", "Dubai"
        ]
        
        # الأجهزة المشبوهة
        self.suspicious_devices = ["جديد", "مشبوه", "new", "suspicious"]
        
    def calculate_risk(self, amount, location, device_type, time_of_day):
        """حساب نسبة المخاطرة"""
        risk_score = 0
        alerts = []
        
        # 1. المبلغ
        if amount >= 47000000:
            risk_score += 45
            alerts.append(f"🚨 مبلغ خطر جداً: {amount:,.0f} UGX")
        elif amount > 10000000:
            risk_score += 30
            alerts.append(f"⚠️ مبلغ كبير: {amount:,.0f} UGX")
        elif amount > 5000000:
            risk_score += 15
            alerts.append(f"⚠️ مبلغ مرتفع: {amount:,.0f} UGX")
        
        # 2. الموقع
        if location in ["Kigali", "Nairobi"]:
            risk_score += 35
            alerts.append(f"🌍 معاملة من {location} – خطر عالي")
        elif location in self.suspicious_locations:
            risk_score += 25
            alerts.append(f"🌍 معاملة من {location}")
        
        # 3. الجهاز
        if device_type in self.suspicious_devices:
            risk_score += 40
            alerts.append(f"📱 جهاز {device_type}")
        
        # 4. الوقت
        late_hours = ["23:00", "00:00", "01:00", "02:00", "03:00", "04:00"]
        if any(h in time_of_day for h in late_hours):
            risk_score += 20
            alerts.append("🕒 وقت غير معتاد")
        
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
        """توصية"""
        if risk_score >= 70:
            return "🚨 **إجراء فوري:** منع المعاملة، إشعار البنك وهيئة الرقابة"
        elif risk_score >= 40:
            return "⚠️ **إجراء تحقق:** طلب تأكيد من العميل"
        else:
            return "✅ **معاملة آمنة:** لا يوجد إجراء مطلوب"
