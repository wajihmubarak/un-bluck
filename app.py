from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
# تفعيل CORS للسماح بالطلبات من الواجهة البرمجية
CORS(app)

# ---------------------------------------------------------
# الإعدادات السرية - المحرك الداخلي (Invisible Logic)
# ---------------------------------------------------------

# السكريبت السري (مخفي تماماً عن المستخدم النهائي)
HIDDEN_TEMPLATE = "Please allow me to access my old account. My account dates back to 2015, and this is my account number +{}"

# القائمة الرسمية لجهات دعم واتساب (Multi-Support)
SUPPORT_EMAILS = [
    "support@whatsapp.com",
    "android@support.whatsapp.com",
    "iphone@support.whatsapp.com",
    "smb@support.whatsapp.com",
    "accessibility@support.whatsapp.com"
]

# عداد نظام التدوير التلقائي (Round Robin)
current_email_index = 0

# ---------------------------------------------------------
# المسارات البرمجية (Routes)
# ---------------------------------------------------------

@app.route('/')
def index():
    """عرض الواجهة الرئيسية"""
    return render_template('index.html')

@app.route('/api/verify_account', methods=['POST'])
def verify_account():
    """التحقق من صحة حساب Gmail و App Password قبل الإضافة"""
    try:
        data = request.json
        email = data.get('e')
        password = data.get('p')

        if not email or not password:
            return jsonify({"status": "error", "message": "بيانات ناقصة"}), 400

        # محاولة تسجيل دخول تجريبية للسيرفر
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email, password)
        
        return jsonify({"status": "success", "message": "تم التحقق من الحساب بنجاح"})
    except smtplib.SMTPAuthenticationError:
        return jsonify({"status": "error", "message": "فشل التحقق: تأكد من App Password"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": f"خطأ غير متوقع: {str(e)}"}), 500

@app.route('/api/send_request', methods=['POST'])
def send_request():
    """تنفيذ بروتوكول الإرسال لفك الحظر بنظام التدوير"""
    global current_email_index
    
    try:
        data = request.json
        all_accounts = data.get('all_accounts')
        target_phone = data.get('phone')

        if not all_accounts or len(all_accounts) == 0:
            return jsonify({"status": "error", "message": "لا توجد محركات إرسال!"}), 400

        # تطبيق نظام التدوير التلقائي للحسابات
        index = current_email_index % len(all_accounts)
        selected_acc = all_accounts[index]
        
        sender_email = selected_acc.get('e')
        app_password = selected_acc.get('p')

        # بناء الرسالة النهائية
        message_content = HIDDEN_TEMPLATE.format(target_phone)

        msg = EmailMessage()
        msg['Subject'] = "Question about WhatsApp"
        msg['From'] = sender_email
        msg['To'] = ", ".join(SUPPORT_EMAILS)
        msg.set_content(message_content)

        # تنفيذ الإرسال الفعلي
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)

        # زيادة العداد للمرة القادمة لضمان التبديل
        current_email_index += 1

        return jsonify({
            "status": "success", 
            "message": f"تم تنفيذ العملية بنجاح عبر المحرك: {sender_email}"
        })

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({"status": "error", "message": "حدث خطأ أثناء الإرسال"}), 500

# ---------------------------------------------------------
# بدء التشغيل
# ---------------------------------------------------------

if __name__ == '__main__':
    # التشغيل على بورت 5000 (الافتراضي لفلاسك)
    app.run(debug=True, port=5000)
