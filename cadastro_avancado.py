import tkinter as tk
from tkinter import messagebox, ttk
import re
from banco import conectar  
from passlib.hash import bcrypt

estados_brasil = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES",
    "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR",
    "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO"
]

def validar_senha(senha):
    if len(senha) < 8:
        return False, "Senha deve ter pelo menos 8 caracteres."
    if not re.search(r'[A-Z]', senha):
        return False, "Senha deve conter ao menos uma letra maiúscula."
    if not re.search(r'[a-z]', senha):
        return False, "Senha deve conter ao menos uma letra minúscula."
    if not re.search(r'[0-9]', senha):
        return False, "Senha deve conter ao menos um número."
    if not re.search(r'[\W_]', senha):
        return False, "Senha deve conter ao menos um símbolo especial."
    return True, ""

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

def cadastrar_usuario():
    nome = entry_nome.get().strip()
    email = entry_email.get().strip()
    senha = entry_senha.get()
    senha_confirma = entry_confirma_senha.get()
    idade = entry_idade.get().strip()
    estado = combo_estado.get().strip()

    if not all([nome, email, senha, senha_confirma, idade, estado]):
        messagebox.showwarning("Aviso", "Preencha todos os campos.")
        return

    if not validar_email(email):
        messagebox.showwarning("Aviso", "Email inválido.")
        return

    if email_existe(email):
        messagebox.showwarning("Aviso", "Este email já está cadastrado.")
        return

    if not validar_idade(idade):
        messagebox.showwarning("Aviso", "Idade inválida. Deve ser numérica e maior ou igual a 13 anos.")
        return

    senha_valida, msg = validar_senha(senha)
    if not senha_valida:
        messagebox.showwarning("Aviso", f"Senha inválida: {msg}")
        return

    if senha != senha_confirma:
        messagebox.showwarning("Aviso", "As senhas não coincidem.")
        return

    try:
        conexao = conectar()
        cursor = conexao.cursor()
        senha_hash = bcrypt.hash(senha)
        cursor.execute('''INSERT INTO usuario (nome, email, senha, idade, estado) 
                          VALUES (?, ?, ?, ?, ?)''', (nome, email, senha_hash, idade, estado))
        conexao.commit()
        messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
        root.destroy()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao cadastrar: {e}")
    finally:
        conexao.close()

root = tk.Tk()
root.title("Cadastro Aprimorado")
root.geometry("350x450")

tk.Label(root, text="Nome:", font=('Arial', 10)).pack(anchor='w', padx=20, pady=2)
entry_nome = tk.Entry(root, font=('Arial', 10))
entry_nome.pack(fill='x', padx=20, pady=5)

tk.Label(root, text="Email:", font=('Arial', 10)).pack(anchor='w', padx=20, pady=2)
entry_email = tk.Entry(root, font=('Arial', 10))
entry_email.pack(fill='x', padx=20, pady=5)

tk.Label(root, text="Senha:", font=('Arial', 10)).pack(anchor='w', padx=20, pady=2)
entry_senha = tk.Entry(root, show="*", font=('Arial', 10))
entry_senha.pack(fill='x', padx=20, pady=5)

tk.Label(root, text="Confirme a Senha:", font=('Arial', 10)).pack(anchor='w', padx=20, pady=2)
entry_confirma_senha = tk.Entry(root, show="*", font=('Arial', 10))
entry_confirma_senha.pack(fill='x', padx=20, pady=5)

tk.Label(root, text="Idade:", font=('Arial', 10)).pack(anchor='w', padx=20, pady=2)
entry_idade = tk.Entry(root, font=('Arial', 10))
entry_idade.pack(fill='x', padx=20, pady=5)

tk.Label(root, text="Estado:", font=('Arial', 10)).pack(anchor='w', padx=20, pady=2)
combo_estado = ttk.Combobox(root, values=estados_brasil, font=('Arial', 10))
combo_estado.pack(fill='x', padx=20, pady=5)

btn_cadastrar = tk.Button(root, text="Cadastrar", command=cadastrar_usuario, font=('Arial', 10))
btn_cadastrar.pack(pady=20)

root.mainloop()
