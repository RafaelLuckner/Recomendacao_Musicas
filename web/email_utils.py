import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_reset_email(email, token):
    reset_link = f"?page=reset_senha&token={token}"
    
    msg = MIMEMultipart()
    msg["From"] = os.getenv("SMTP_FROM")
    msg["To"] = email
    msg["Subject"] = "Redefinição de Senha - M4U"
    
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <img src="https://exemplo.com/logo_m4u.png" alt="M4U Logo" style="max-width: 200px; margin-bottom: 20px;">
                <h2 style="color: #FF6B00;">Redefinição de Senha</h2>
                <p>Recebemos uma solicitação para redefinir a senha da sua conta M4U.</p>
                <p>Clique no botão abaixo para criar uma nova senha:</p>
                <a href="{reset_link}" style="display: inline-block; padding: 10px 20px; background-color: #FF6B00; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0;">Redefinir Senha</a>
                <p>Se você não solicitou esta redefinição, por favor ignore este e-mail.</p>
                <p style="font-size: 12px; color: #777;">Este link expirará em 24 horas.</p>
            </div>
        </body>
    </html>
    """
    
    msg.attach(MIMEText(body, "html"))
    
    try:
        with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
            server.starttls()
            server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {str(e)}")
        return False