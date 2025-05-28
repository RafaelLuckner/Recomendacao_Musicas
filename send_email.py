import yagmail

def enviar_email_token(destinatario: str, token: str):
    """
    Envia um e-mail com o token de recuperação de senha via Yagmail (Gmail).
    
    Parâmetros:
        destinatario (str): E-mail do usuário.
        token (str): Token gerado para recuperação.
    """
    # Configurações do Gmail
    EMAIL_REMETENTE = "@gmail.com"
    SENHA_APP = ""  # Senha de app do Gmail (obrigatório)

    # Conteúdo do e-mail (HTML e texto alternativo)
    assunto = "🔑 Token de Recuperação de Senha"
    
    mensagem_html = f"""
    <html>
        <body>
            <h2>Recuperação de Senha</h2>
            <p>Seu token: <strong>{token}</strong></p>
            <p><small>Validade: 1 hora.</small></p>
        </body>
    </html>
    """
    
    mensagem_texto = f"Use este token para redefinir sua senha: {token} (Validade: 1 hora)"

    try:
        # Inicializa o cliente Yagmail
        yag = yagmail.SMTP(user=EMAIL_REMETENTE, password=SENHA_APP)
        
        # Envia o e-mail (HTML + texto alternativo)
        yag.send(
            to=destinatario,
            subject=assunto,
            contents=[mensagem_texto, mensagem_html]  # yagmail alterna automaticamente entre texto/HTML
        )
        
        print("✅ E-mail enviado com sucesso!")
    except Exception as e:
        print(f"❌ Falha no envio: {e}")

# Exemplo de uso:
enviar_email_token("rafellucknr3@gmail.com", "ABCD1234EFGH5678")