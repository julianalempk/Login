rom flask import Flask, render_template, request, url_for, redirect, flash
from flask_mail import Mail, Message
import secrets
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta' # Substitua por uma chave secreta forte

# Configuração do Flask-Mail (adapte com suas informações)
app.config['MAIL_SERVER'] = 'smtp.seudominio.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'seu_email@seudominio.com'
app.config['MAIL_PASSWORD'] = 'sua_senha_de_email'
app.config['MAIL_DEFAULT_SENDER'] = 'seu_email@seudominio.com'

mail = Mail(app)

# Simulação de um banco de dados de usuários (substitua pelo seu banco de dados real)
usuarios = {
    'teste@email.com': {'senha': 'senha123', 'token_reset_senha': None, 'token_expiracao': None}
}

def gerar_token_reset():
    return secrets.token_urlsafe(16)

def enviar_email_reset_senha(email, token):
    msg = Message('Redefinição de Senha', recipients=[email])
    link_redefinicao = url_for('redefinir_senha', token=token, _external=True)
    msg.body = f'Clique no link abaixo para redefinir sua senha:\n\n{link_redefinicao}\n\nEste link é válido por 1 hora.'
    mail.send(msg)

@app.route('/esqueci_senha', methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = request.form['email']
        if email in usuarios:
            token = gerar_token_reset()
            usuarios[email]['token_reset_senha'] = token
            usuarios[email]['token_expiracao'] = datetime.utcnow() + timedelta(hours=1)
            enviar_email_reset_senha(email, token)
            flash('Um link para redefinição de senha foi enviado para o seu e-mail.', 'info')
            return redirect(url_for('login'))
        else:
            flash('Não encontramos um usuário com este e-mail.', 'danger')
    return render_template('esqueci_senha.html')

@app.route('/redefinir_senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    for email, dados in usuarios.items():
        if dados['token_reset_senha'] == token and dados['token_expiracao'] > datetime.utcnow():
            if request.method == 'POST':
                nova_senha = request.form['nova_senha']
                confirmar_nova_senha = request.form['confirmar_nova_senha']
                if nova_senha == confirmar_nova_senha:
                    usuarios[email]['senha'] = nova_senha # Aqui você hasharia a senha real
                    usuarios[email]['token_reset_senha'] = None
                    usuarios[email]['token_expiracao'] = None
                    flash('Sua senha foi redefinida com sucesso. Faça login com a nova senha.', 'success')
                    return redirect(url_for('login'))
                else:
                    flash('As novas senhas não coincidem.', 'danger')
                return render_template('redefinir_senha.html')
            return render_template('redefinir_senha.html')
    flash('Este link de redefinição de senha é inválido ou expirou.', 'danger')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        if email in usuarios and usuarios[email]['senha'] == senha: # Substitua pela sua lógica de autenticação
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('pagina_principal'))
        else:
            flash('Credenciais inválidas.', 'danger')
    return render_template('index.html') # Assumindo que seu formulário de login está em index.html

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    # Sua lógica de registro aqui
    return render_template('registro.html') # Seu formulário de registro

@app.route('/pagina_principal')
def pagina_principal():
    return "Página Principal"

if __name__ == '__main__':
    app.run(debug=True)