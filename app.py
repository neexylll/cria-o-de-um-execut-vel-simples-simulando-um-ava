import tkinter as tk
from tkinter import messagebox, ttk
import re
import subprocess
from banco import conectar, inicializador_do_banco
from passlib.hash import bcrypt
import webbrowser
import questionario  

modo_noturno = False
timer_id = None

def validar_senha(senha):
    return (len(senha) >= 8 and
            re.search(r'[A-Z]', senha) and
            re.search(r'[a-z]', senha) and
            re.search(r'[0-9]', senha) and
            re.search(r'[\W_]', senha))

def validar_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validar_idade(idade_str):
    if not idade_str.isdigit():
        return False
    idade = int(idade_str)
    return idade >= 13

def email_existe(email):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT 1 FROM usuario WHERE email=?", (email,))
    existe = cursor.fetchone() is not None
    conexao.close()
    return existe

def aplicar_tema(janela):
    global modo_noturno
    if modo_noturno:
        bg = '#222222'
        fg = '#eeeeee'
        btn_bg = '#444444'
        btn_fg = '#eeeeee'
        entry_bg = '#333333'
        entry_fg = '#eeeeee'
    else:
        bg = 'white'
        fg = 'black'
        btn_bg = 'black'
        btn_fg = 'white'
        entry_bg = 'white'
        entry_fg = 'black'

    janela.configure(bg=bg)
    for widget in janela.winfo_children():
        tipo = widget.winfo_class()
        if tipo == 'Label':
            widget.configure(bg=bg, fg=fg)
        elif tipo == 'Button':
            widget.configure(bg=btn_bg, fg=btn_fg, activebackground=btn_bg)
            aplicar_hover(widget, modo_noturno)
        elif tipo in ['Entry', 'TEntry']:
            widget.configure(bg=entry_bg, fg=entry_fg, insertbackground=fg)
        elif tipo == 'Text':
            widget.configure(bg=entry_bg, fg=entry_fg, insertbackground=fg)

def aplicar_hover(botao, modo_noturno_local):
    def on_enter(event):
        if modo_noturno_local:
            event.widget['background'] = '#666666'
            event.widget['foreground'] = '#ffffff'
        else:
            event.widget['background'] = '#444444'
            event.widget['foreground'] = '#ffffff'
    def on_leave(event):
        if modo_noturno_local:
            event.widget['background'] = '#444444'
            event.widget['foreground'] = '#eeeeee'
        else:
            event.widget['background'] = 'black'
            event.widget['foreground'] = 'white'
    botao.bind("<Enter>", on_enter)
    botao.bind("<Leave>", on_leave)

def alternar_modo_noturno(janela):
    global modo_noturno
    modo_noturno = not modo_noturno
    aplicar_tema(janela)

def iniciar_timer_inatividade(root):
    global timer_id
    TIMEOUT = 3600 * 1000  

    def encerrar_por_inatividade():
        messagebox.showinfo("Encerrando", "O programa será fechado por inatividade.")
        root.quit()

    def resetar_timer(event=None):
        global timer_id
        if timer_id is not None:
            root.after_cancel(timer_id)
        timer_id = root.after(TIMEOUT, encerrar_por_inatividade)

    root.bind_all("<Any-KeyPress>", resetar_timer)
    root.bind_all("<Any-Button>", resetar_timer)
    root.bind_all("<Motion>", resetar_timer)

    resetar_timer()

def abrir_tela_cadastro():
    def cadastrar_usuario():
        nome = entry_nome.get().strip()
        email = entry_email.get().strip()
        senha = entry_senha.get()
        idade = entry_idade.get().strip()
        estado = combo_estado.get().strip()

        if not all([nome, email, senha, idade, estado]):
            messagebox.showwarning("Aviso", "Preencha todos os campos")
            return

        if not validar_email(email):
            messagebox.showwarning("Aviso", "Email inválido.")
            return

        if not validar_idade(idade):
            messagebox.showwarning("Aviso", "Idade inválida. Deve ser numérica e maior ou igual a 13 anos.")
            return

        if email_existe(email):
            messagebox.showwarning("Aviso", "Este email já está cadastrado.")
            return

        if not validar_senha(senha):
            messagebox.showwarning("Aviso", "Senha fraca! Use letras maiúsculas, minúsculas, números e símbolos.")
            return

        try:
            conexao = conectar()
            cursor = conexao.cursor()
            senha_hash = bcrypt.hash(senha)
            cursor.execute('''INSERT INTO usuario (nome, email, senha, idade, estado) 
                              VALUES (?, ?, ?, ?, ?)''', (nome, email, senha_hash, idade, estado))
            conexao.commit()
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            janela_cadastro.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar: {e}")
        finally:
            conexao.close()

    janela_cadastro = tk.Toplevel()
    janela_cadastro.title("Cadastro")
    janela_cadastro.geometry("350x400")

    campos = [("Nome", 'nome'), ("Email", 'email'), ("Senha", 'senha'), ("Idade", 'idade'), ("Estado", 'estado')]
    entries = {}

    for texto, chave in campos:
        lbl = tk.Label(janela_cadastro, text=texto + ": ", font=('Arial', 10))
        lbl.pack(anchor='w', padx=20, pady=2)
        if chave == 'estado':
            combo_estado = ttk.Combobox(janela_cadastro, values=estados_brasil, font=('Arial', 10))
            combo_estado.pack(fill='x', padx=20, pady=5)
        elif chave == 'senha':
            entry = tk.Entry(janela_cadastro, show="*", font=('Arial', 10))
            entry.pack(fill='x', padx=20, pady=5)
            entries[chave] = entry
        else:
            entry = tk.Entry(janela_cadastro, font=('Arial', 10))
            entry.pack(fill='x', padx=20, pady=5)
            entries[chave] = entry

    entry_nome = entries['nome']
    entry_email = entries['email']
    entry_senha = entries['senha']
    entry_idade = entries['idade']

    btn = tk.Button(janela_cadastro, text="Cadastrar", command=cadastrar_usuario, font=('Arial', 10))
    btn.pack(pady=20)
    aplicar_tema(janela_cadastro)

def abrir_perfil(nome_usuario):
    perfil_janela = tk.Toplevel()
    perfil_janela.title("Perfil")
    perfil_janela.geometry("300x400")

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT nome, email, idade, estado FROM usuario WHERE nome=?", (nome_usuario,))
    usuario = cursor.fetchone()
    conexao.close()

    labels = ["Nome", "Email", "Senha", "Idade", "Estado"]
    entries = {}

    for idx, campo in enumerate(labels):
        lbl = tk.Label(perfil_janela, text=campo + ": ", font=('Arial', 10))
        lbl.pack(anchor='w', padx=20, pady=2)
        entry = tk.Entry(perfil_janela, font=('Arial', 10))
        entry.pack(fill='x', padx=20, pady=5)
        if campo == "Senha":
            entry.insert(0, "")
        else:
            entry.insert(0, usuario[idx if campo != "Senha" else idx - 1])
        entries[campo] = entry

    def salvar_perfil():
        novo_nome = entries["Nome"].get().strip()
        novo_email = entries["Email"].get().strip()
        nova_senha = entries["Senha"].get()
        nova_idade = entries["Idade"].get().strip()
        novo_estado = entries["Estado"].get().strip()

        if not all([novo_nome, novo_email, nova_idade, novo_estado]):
            messagebox.showwarning("Aviso", "Preencha todos os campos exceto senha, se não quiser alterá-la.")
            return

        if not validar_email(novo_email):
            messagebox.showwarning("Aviso", "Email inválido.")
            return

        if not validar_idade(nova_idade):
            messagebox.showwarning("Aviso", "Idade inválida. Deve ser numérica e maior ou igual a 13 anos.")
            return

        try:
            conexao = conectar()
            cursor = conexao.cursor()
            if nova_senha:
                senha_hash = bcrypt.hash(nova_senha)
                cursor.execute('''UPDATE usuario SET nome=?, email=?, senha=?, idade=?, estado=? WHERE nome=?''',
                               (novo_nome, novo_email, senha_hash, nova_idade, novo_estado, nome_usuario))
            else:
                cursor.execute('''UPDATE usuario SET nome=?, email=?, idade=?, estado=? WHERE nome=?''',
                               (novo_nome, novo_email, nova_idade, novo_estado, nome_usuario))
            conexao.commit()
            messagebox.showinfo("Sucesso", "Perfil atualizado!")
            perfil_janela.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar: {e}")
        finally:
            conexao.close()

    btn_salvar = tk.Button(perfil_janela, text="Salvar", command=salvar_perfil, font=('Arial', 10))
    btn_salvar.pack(pady=20)

    aplicar_tema(perfil_janela)

def buscar_cursos():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, titulo, conteudo FROM cursos")
    cursos = cursor.fetchall()
    conexao.close()
    return cursos

def buscar_aulas_por_curso(curso_id):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, titulo, video FROM aulas WHERE curso_id=?", (curso_id,))
    aulas = cursor.fetchall()
    conexao.close()
    return aulas

def abrir_cursos(janela_pai):
    cursos = buscar_cursos()

    cursos_janela = tk.Toplevel(janela_pai)
    cursos_janela.title("Cursos Disponíveis")
    cursos_janela.geometry("400x400")

    lbl = tk.Label(cursos_janela, text="Selecione um curso para ver as aulas:", font=('Arial', 12))
    lbl.pack(pady=10)

    for curso in cursos:
        curso_id, titulo, conteudo = curso

        def abrir_aulas(curso_id=curso_id, titulo_curso=titulo, conteudo_curso=conteudo):
            curso_janela = tk.Toplevel(cursos_janela)
            curso_janela.title(f"Aulas - {titulo_curso}")
            curso_janela.geometry("400x400")

            lbl_titulo = tk.Label(curso_janela, text=f"Aulas do curso: {titulo_curso}", font=('Arial', 14, 'bold'))
            lbl_titulo.pack(pady=10)

            lbl_conteudo = tk.Label(curso_janela, text=conteudo_curso, wraplength=380)
            lbl_conteudo.pack(pady=5)

            aulas = buscar_aulas_por_curso(curso_id)

            for aula in aulas:
                aula_id, aula_titulo, video = aula
                btn_aula = tk.Button(curso_janela, text=aula_titulo, font=('Arial', 10),
                                     command=lambda v=video: abrir_video(v))
                btn_aula.pack(fill='x', padx=10, pady=3)

            aplicar_tema(curso_janela)

        btn_curso = tk.Button(cursos_janela, text=titulo, font=('Arial', 12), command=abrir_aulas)
        btn_curso.pack(fill='x', padx=20, pady=5)

    def fechar_cursos():
        cursos_janela.destroy()

    cursos_janela.protocol("WM_DELETE_WINDOW", fechar_cursos)

    aplicar_tema(cursos_janela)

def abrir_video(video_url):
    try:
        webbrowser.open(video_url)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao abrir vídeo: {e}")

def abrir_tela_opcoes(nome_usuario):
    janela_login.withdraw()

    tela_opcoes = tk.Toplevel()
    tela_opcoes.title(f"Bem-vindo, {nome_usuario}")
    tela_opcoes.geometry("500x450")

    lbl_msg = tk.Label(tela_opcoes, text=f"Bem-vindo, {nome_usuario}!", font=('Arial', 14))
    lbl_msg.pack(pady=20)

    btn_cursos = tk.Button(tela_opcoes, text="Ver Cursos", font=('Arial', 12),
                           command=lambda: abrir_cursos(tela_opcoes))
    btn_cursos.pack(pady=10)

    btn_perfil = tk.Button(tela_opcoes, text="Perfil", font=('Arial', 12),
                           command=lambda: abrir_perfil(nome_usuario))
    btn_perfil.pack(pady=10)

    btn_questionario = tk.Button(tela_opcoes, text="Questionário", font=('Arial', 12),
                                command=lambda: questionario.abrir_questionario(nome_usuario))
    btn_questionario.pack(pady=10)

    btn_modo = tk.Button(tela_opcoes, text="Modo Noturno", font=('Arial', 12),
                         command=lambda: alternar_modo_noturno(tela_opcoes))
    btn_modo.pack(pady=10)

    btn_sair = tk.Button(tela_opcoes, text="Sair", font=('Arial', 12), command=lambda: sair(tela_opcoes))
    btn_sair.pack(pady=10)

    aplicar_tema(tela_opcoes)
    iniciar_timer_inatividade(tela_opcoes)

def sair(janela):
    janela.destroy()
    janela_login.deiconify()

def fazer_login():
    email = entry_email_login.get().strip()
    senha = entry_senha_login.get()

    if not email or not senha:
        messagebox.showwarning("Aviso", "Preencha email e senha")
        return

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT nome, senha FROM usuario WHERE email=?", (email,))
    resultado = cursor.fetchone()
    conexao.close()

    if resultado:
        nome_usuario, senha_hash = resultado
        if bcrypt.verify(senha, senha_hash):
            abrir_tela_opcoes(nome_usuario)
        else:
            messagebox.showerror("Erro", "Senha incorreta")
    else:
        messagebox.showerror("Erro", "Usuário não encontrado")

def criar_banco():
    try:
        inicializador_do_banco()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao inicializar banco: {e}")

estados_brasil = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO"
]

janela_login = tk.Tk()
janela_login.title("Tela de Login")
janela_login.geometry("350x350")

lbl_email_login = tk.Label(janela_login, text="Email:", font=('Arial', 12))
lbl_email_login.pack(pady=10)

entry_email_login = tk.Entry(janela_login, font=('Arial', 12))
entry_email_login.pack(pady=5)

lbl_senha_login = tk.Label(janela_login, text="Senha:", font=('Arial', 12))
lbl_senha_login.pack(pady=10)

entry_senha_login = tk.Entry(janela_login, show="*", font=('Arial', 12))
entry_senha_login.pack(pady=5)

btn_login = tk.Button(janela_login, text="Login", command=fazer_login, font=('Arial', 12))
btn_login.pack(pady=20)

btn_cadastro = tk.Button(janela_login, text="Cadastro", command=abrir_tela_cadastro, font=('Arial', 12))
btn_cadastro.pack(pady=5)

btn_criar_banco = tk.Button(janela_login, text="Criar Banco de Dados", command=criar_banco, font=('Arial', 12))
btn_criar_banco.pack(pady=5)

aplicar_tema(janela_login)
iniciar_timer_inatividade(janela_login)

janela_login.mainloop()
