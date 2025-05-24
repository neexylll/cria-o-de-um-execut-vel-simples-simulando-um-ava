import tkinter as tk
from tkinter import ttk, messagebox
from banco import conectar

# Função para limpar widgets do frame
def limpar_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def abrir_questionario(nome_usuario):
    janela_q = tk.Toplevel()
    janela_q.title(f"Questionários - {nome_usuario}")
    janela_q.geometry("600x500")

    frame_principal = ttk.Frame(janela_q)
    frame_principal.pack(fill="both", expand=True, padx=10, pady=10)

    estado = {
        "curso_id": None,
        "aula_id": None,
        "questionario_id": None,
        "respostas_usuario": {}
    }

    def mostrar_cursos():
        limpar_frame(frame_principal)
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("SELECT id, titulo FROM cursos")
        cursos = cursor.fetchall()
        conexao.close()

        lbl = ttk.Label(frame_principal, text="Selecione um curso:", font=("Arial", 14))
        lbl.pack(pady=10)

        for cid, titulo in cursos:
            btn = ttk.Button(frame_principal, text=titulo,
                             command=lambda c=cid: selecionar_curso(c))
            btn.pack(fill='x', pady=5)

    def selecionar_curso(curso_id):
        estado["curso_id"] = curso_id
        mostrar_aulas(curso_id)

    def mostrar_aulas(curso_id):
        limpar_frame(frame_principal)
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("SELECT id, titulo FROM aulas WHERE curso_id=?", (curso_id,))
        aulas = cursor.fetchall()
        conexao.close()

        lbl = ttk.Label(frame_principal, text="Selecione uma aula:", font=("Arial", 14))
        lbl.pack(pady=10)

        for aid, titulo in aulas:
            btn = ttk.Button(frame_principal, text=titulo,
                             command=lambda a=aid: selecionar_aula(a))
            btn.pack(fill='x', pady=5)

        btn_voltar = ttk.Button(frame_principal, text="Voltar para Cursos", command=mostrar_cursos)
        btn_voltar.pack(pady=15)

    def selecionar_aula(aula_id):
        estado["aula_id"] = aula_id
        mostrar_questionario(aula_id)

    def mostrar_questionario(aula_id):
        limpar_frame(frame_principal)
        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute("SELECT id, titulo FROM questionarios WHERE aula_id=?", (aula_id,))
        result = cursor.fetchone()
        if not result:
            messagebox.showinfo("Info", "Nenhum questionário para esta aula.")
            mostrar_aulas(estado["curso_id"])
            return

        q_id, q_titulo = result
        estado["questionario_id"] = q_id

        lbl = ttk.Label(frame_principal, text=q_titulo, font=("Arial", 16, "bold"))
        lbl.pack(pady=10)

        cursor.execute("SELECT id, texto FROM perguntas WHERE questionario_id=?", (q_id,))
        perguntas = cursor.fetchall()

        estado["respostas_usuario"] = {}

        for pergunta_id, texto_pergunta in perguntas:
            ttk.Label(frame_principal, text=texto_pergunta, font=("Arial", 12)).pack(anchor='w', pady=5)

            cursor.execute("SELECT id, texto FROM respostas WHERE pergunta_id=?", (pergunta_id,))
            respostas = cursor.fetchall()

            var_resposta = tk.StringVar()
            estado["respostas_usuario"][pergunta_id] = var_resposta

            for resposta_id, texto_resposta in respostas:
                rb = ttk.Radiobutton(frame_principal, text=texto_resposta, variable=var_resposta, value=str(resposta_id))
                rb.pack(anchor='w', padx=20)

        btn_enviar = ttk.Button(frame_principal, text="Enviar Respostas", command=lambda: enviar_respostas(nome_usuario))
        btn_enviar.pack(pady=15)

        btn_voltar = ttk.Button(frame_principal, text="Voltar para Aulas", command=lambda: mostrar_aulas(estado["curso_id"]))
        btn_voltar.pack()

        conexao.close()

    def enviar_respostas(nome_usuario):
        conexao = conectar()
        cursor = conexao.cursor()

        q_id = estado["questionario_id"]
        respostas_usuario = estado["respostas_usuario"]

        if not respostas_usuario:
            messagebox.showwarning("Aviso", "Não há perguntas para responder.")
            return

        for pergunta_id, var_resposta in respostas_usuario.items():
            if var_resposta.get() == "":
                messagebox.showwarning("Aviso", "Por favor, responda todas as perguntas.")
                return

        cursor.execute("""
            SELECT pergunta_id, id FROM respostas WHERE pergunta_id IN (
                SELECT id FROM perguntas WHERE questionario_id=?
            ) AND correta=1
        """, (q_id,))
        respostas_certas = cursor.fetchall()

        acertos = 0
        total = len(respostas_usuario)

        for pergunta_id, resposta_correta_id in respostas_certas:
            resposta_usuario = respostas_usuario[pergunta_id].get()
            if resposta_usuario == str(resposta_correta_id):
                acertos += 1

        nota = round((acertos / total) * 10, 2)
        messagebox.showinfo("Resultado", f"Você acertou {acertos} de {total} perguntas. Nota: {nota}")

        cursor.execute("SELECT id FROM usuario WHERE nome=?", (nome_usuario,))
        usuario = cursor.fetchone()
        if usuario:
            usuario_id = usuario[0]
            cursor.execute("INSERT INTO notas (usuario_id, aula_id, nota) VALUES (?, ?, ?)",
                           (usuario_id, estado["aula_id"], nota))
            conexao.commit()

        conexao.close()
        mostrar_cursos()

    mostrar_cursos()
    janela_q.transient()
    janela_q.grab_set()
    janela_q.focus_force()

def abrir_notas(nome_usuario):
    janela_notas = tk.Toplevel()
    janela_notas.title(f"Notas de {nome_usuario}")
    janela_notas.geometry("400x400")

    frame = ttk.Frame(janela_notas)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT id FROM usuario WHERE nome=?", (nome_usuario,))
    usuario = cursor.fetchone()
    if not usuario:
        messagebox.showerror("Erro", "Usuário não encontrado.")
        return
    usuario_id = usuario[0]

    cursor.execute('''
        SELECT aulas.titulo, notas.nota
        FROM notas
        JOIN aulas ON notas.aula_id = aulas.id
        WHERE notas.usuario_id = ?
    ''', (usuario_id,))
    resultados = cursor.fetchall()

    total = 0
    count = 0

    ttk.Label(frame, text="Suas Notas:", font=("Arial", 14)).pack(pady=10)

    for aula, nota in resultados:
        ttk.Label(frame, text=f"{aula}: {nota}").pack(anchor='w', padx=10)
        total += nota
        count += 1

    if count > 0:
        media = round(total / count, 2)
        ttk.Label(frame, text=f"Média Geral: {media}", font=("Arial", 12, "bold")).pack(pady=20)
    else:
        ttk.Label(frame, text="Nenhuma nota registrada ainda.").pack(pady=20)

    conexao.close()
