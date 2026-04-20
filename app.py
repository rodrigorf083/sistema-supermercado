from flask import Flask, request, redirect
import mysql.connector

app = Flask(__name__)

# 🔗 CONEXÃO MYSQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",  # sua senha
    database="supermercado"
)

cursor = db.cursor(dictionary=True)

usuario = {"email": "admin", "senha": "123"}

# 🎨 LAYOUT (SEU ORIGINAL PRESERVADO)
def layout(conteudo):
    return f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial;
                background: #005CA9;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }}
            .box {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
                width: 320px;
                box-shadow: 0px 0px 10px rgba(0,0,0,0.3);
            }}
            input {{
                margin: 10px;
                padding: 10px;
                width: 90%;
            }}
            button {{
                padding: 10px;
                width: 95%;
                background: #005CA9;
                color: white;
                border: none;
                border-radius: 5px;
            }}
            a {{
                display: block;
                margin: 10px;
                padding: 10px;
                background: #005CA9;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="box">
            {conteudo}
        </div>
    </body>
    </html>
    """

# 🔐 LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["email"] == usuario["email"] and request.form["senha"] == usuario["senha"]:
            return redirect("/home")
        else:
            return layout("<h3>Login inválido</h3>")

    return layout("""
        <h2>🛒 Supermercado Unifacisa</h2>
        <form method="post">
            <input name="email" placeholder="Email">
            <input name="senha" type="password" placeholder="Senha">
            <button>Entrar</button>
        </form>
    """)

# 🏠 HOME
@app.route("/home")
def home():
    return layout("""
        <h2>🏠 Menu</h2>
        <a href="/produtos">📦 Produtos</a>
        <a href="/usuarios">👤 Usuários</a>
        <a href="/clientes">👥 Clientes</a>
    """)

# =========================
# 👤 USUÁRIOS
# =========================
@app.route("/usuarios")
def usuarios_page():
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()

    html = "<h2>👤 Usuários</h2>"
    for u in usuarios:
        html += f"""
        <p>
            <a href='/ver_user/{u['id']}'>{u['nome']}</a>
            <a href='/edit_user/{u['id']}'>✏️</a>
            <a href='/del_user/{u['id']}'>❌</a>
        </p>
        """

    html += "<a href='/add_user'>Adicionar</a><a href='/home'>Voltar</a>"
    return layout(html)

@app.route("/add_user", methods=["GET","POST"])
def add_user():
    if request.method == "POST":
        cursor.execute(
            "INSERT INTO usuarios (nome,email,cpf,senha) VALUES (%s,%s,%s,%s)",
            (
                request.form["nome"],
                request.form["email"],
                request.form["cpf"],
                request.form["senha"]
            )
        )
        db.commit()
        return redirect("/usuarios")

    return layout("""
        <h2>➕ Usuário</h2>
        <form method="post">
            <input name="nome" placeholder="Nome">
            <input name="email" placeholder="Email">
            <input name="cpf" placeholder="CPF">
            <input name="senha" placeholder="Senha">
            <button>Salvar</button>
        </form>
    """)

@app.route("/del_user/<int:id>")
def del_user(id):
    cursor.execute("DELETE FROM usuarios WHERE id=%s",(id,))
    db.commit()
    return redirect("/usuarios")

@app.route("/edit_user/<int:id>", methods=["GET","POST"])
def edit_user(id):
    if request.method == "POST":
        cursor.execute(
            "UPDATE usuarios SET nome=%s,email=%s,cpf=%s,senha=%s WHERE id=%s",
            (
                request.form["nome"],
                request.form["email"],
                request.form["cpf"],
                request.form["senha"],
                id
            )
        )
        db.commit()
        return redirect("/usuarios")

    cursor.execute("SELECT * FROM usuarios WHERE id=%s",(id,))
    u = cursor.fetchone()

    return layout(f"""
        <h2>✏️ Editar Usuário</h2>
        <form method="post">
            <input name="nome" value="{u['nome']}">
            <input name="email" value="{u['email']}">
            <input name="cpf" value="{u['cpf']}">
            <input name="senha" value="{u['senha']}">
            <button>Salvar</button>
        </form>
    """)

@app.route("/ver_user/<int:id>")
def ver_user(id):
    cursor.execute("SELECT * FROM usuarios WHERE id=%s", (id,))
    u = cursor.fetchone()

    return layout(f"""
        <h2>👤 Detalhes</h2>

        <p><b>Nome:</b> {u['nome']}</p>
        <p><b>Email:</b> {u['email']}</p>
        <p><b>CPF:</b> {u['cpf']}</p>
        <p><b>Senha:</b> {u['senha']}</p>

        <a href="/usuarios">Voltar</a>
    """)

# =========================
# 📦 PRODUTOS
# =========================
@app.route("/produtos")
def produtos():
    cursor.execute("SELECT * FROM produtos")
    dados = cursor.fetchall()

    html = "<h2>📦 Produtos</h2>"
    for p in dados:
        preco = p["preco"]
        if p["promo"]:
            preco = f"<s>{p['preco']}</s> ➜ {p['promo']}"

        html += f"""
        <p>
            {p['nome']} - {preco}
            <a href='/promo/{p['id']}'>💸</a>
            <a href='/del_prod/{p['id']}'>❌</a>
        </p>
        """

    html += "<a href='/add_prod'>Adicionar</a><a href='/home'>Voltar</a>"
    return layout(html)

@app.route("/add_prod", methods=["GET","POST"])
def add_prod():
    if request.method == "POST":
        cursor.execute(
            "INSERT INTO produtos (nome,preco,promo) VALUES (%s,%s,%s)",
            (request.form["nome"], request.form["preco"], "")
        )
        db.commit()
        return redirect("/produtos")

    return layout("""
        <h2>➕ Produto</h2>
        <form method="post">
            <input name="nome" placeholder="Nome">
            <input name="preco" placeholder="Preço">
            <button>Salvar</button>
        </form>
    """)

@app.route("/del_prod/<int:id>")
def del_prod(id):
    cursor.execute("DELETE FROM produtos WHERE id=%s",(id,))
    db.commit()
    return redirect("/produtos")

@app.route("/promo/<int:id>", methods=["GET","POST"])
def promo(id):
    if request.method == "POST":
        cursor.execute(
            "UPDATE produtos SET promo=%s WHERE id=%s",
            (request.form["promo"], id)
        )
        db.commit()
        return redirect("/produtos")

    return layout("""
        <h2>💸 Promoção</h2>
        <form method="post">
            <input name="promo" placeholder="Novo preço">
            <button>Salvar</button>
        </form>
    """)

# =========================
# 👥 CLIENTES
# =========================
@app.route("/clientes")
def clientes():
    cursor.execute("SELECT * FROM clientes")
    dados = cursor.fetchall()

    html = "<h2>👥 Clientes</h2>"
    for c in dados:
        html += f"""
        <p>
            <a href='/ver_cliente/{c['id']}'>{c['nome']}</a>
            <a href='/edit_cliente/{c['id']}'>✏️</a>
            <a href='/del_cliente/{c['id']}'>❌</a>
        </p>
        """

    html += "<a href='/add_cliente'>Adicionar</a><a href='/home'>Voltar</a>"
    return layout(html)

@app.route("/add_cliente", methods=["GET","POST"])
def add_cliente():
    if request.method == "POST":
        cursor.execute(
            "INSERT INTO clientes (nome,cpf,idade,telefone) VALUES (%s,%s,%s,%s)",
            (
                request.form["nome"],
                request.form["cpf"],
                request.form["idade"],
                request.form["telefone"]
            )
        )
        db.commit()
        return redirect("/clientes")

    return layout("""
        <h2>➕ Cliente</h2>
        <form method="post">
            <input name="nome" placeholder="Nome">
            <input name="cpf" placeholder="CPF">
            <input name="idade" placeholder="Idade">
            <input name="telefone" placeholder="Telefone">
            <button>Salvar</button>
        </form>
    """)

@app.route("/del_cliente/<int:id>")
def del_cliente(id):
    cursor.execute("DELETE FROM clientes WHERE id=%s",(id,))
    db.commit()
    return redirect("/clientes")

@app.route("/edit_cliente/<int:id>", methods=["GET","POST"])
def edit_cliente(id):
    if request.method == "POST":
        cursor.execute(
            "UPDATE clientes SET nome=%s,cpf=%s,idade=%s,telefone=%s WHERE id=%s",
            (
                request.form["nome"],
                request.form["cpf"],
                request.form["idade"],
                request.form["telefone"],
                id
            )
        )
        db.commit()
        return redirect("/clientes")

    cursor.execute("SELECT * FROM clientes WHERE id=%s",(id,))
    c = cursor.fetchone()

    return layout(f"""
        <h2>✏️ Editar Cliente</h2>
        <form method="post">
            <input name="nome" value="{c['nome']}">
            <input name="cpf" value="{c['cpf']}">
            <input name="idade" value="{c['idade']}">
            <input name="telefone" value="{c['telefone']}">
            <button>Salvar</button>
        </form>
    """)

@app.route("/ver_cliente/<int:id>")
def ver_cliente(id):
    cursor.execute("SELECT * FROM clientes WHERE id=%s",(id,))
    c = cursor.fetchone()

    return layout(f"""
        <h2>👥 Detalhes</h2>
        <p>{c['nome']}</p>
        <p>{c['cpf']}</p>
        <p>{c['idade']}</p>
        <p>{c['telefone']}</p>
        <a href="/clientes">Voltar</a>
    """)

app.run(debug=True)