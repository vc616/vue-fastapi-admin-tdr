import asyncio
import random
import smtplib
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.settings import settings


def generate_verify_code(length: int = 6) -> str:
    """生成随机验证码"""
    return ''.join(random.choices(string.digits, k=length))


def send_verify_code_email(to_email: str, code: str) -> bool:
    """发送验证码邮件"""
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = '密码重置验证码'

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #1a1a2e;">密码重置验证码</h2>
            <p>您好，</p>
            <p>您收到了这封邮件是因为有人请求重置您的账户密码。</p>
            <div style="background: #f5f6fb; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <p style="font-size: 24px; font-weight: bold; color: #1a1a2e; margin: 0; text-align: center;">
                    {code}
                </p>
            </div>
            <p>验证码有效期为 <strong>5 分钟</strong>，请勿将验证码告诉他人。</p>
            <p>如果您没有请求重置密码，请忽略此邮件。</p>
            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
            <p style="color: #6b7280; font-size: 12px;">
                此邮件由系统自动发送，请勿回复。
            </p>
        </div>
        """

        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.starttls()
            server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, [to_email], msg.as_string())

        return True
    except Exception as e:
        print(f"发送邮件失败: {e}")
        return False
