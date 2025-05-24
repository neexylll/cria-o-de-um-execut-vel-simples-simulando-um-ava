import tkinter as tk
from tkinter import ttk
from banco import conectar

# As matérias que você pediu
MATERIAS = [
    "Matemática e Estatística",
    "Infraestrutura Computacional",
    "Tecnologia da Informação",
    "Lei Geral de Proteção de Dados",
    "Cyber Segurança"
]

def pegar_notas_por_materia(nome_usuario, materia):
    conexao = conectar()
    cursor = conexao.cursor()
    # Pegamos as notas de questionários relacionados a essa matéria para o usuário
    cursor.execute("""
        SELECT q.nome, n.nota FROM nota n
        JOIN questionario q ON n.id_questionario = q.id
        JOIN usuario u ON n.id_usuario = u.id
        WHERE u.nome = ? AND q.materia = ?
    """, (nome_usuario, materia))
    resultados = cursor.fetchall()
    conexao.close()
    return resultados

def calcular_media(notas):
    if not notas:
        return 0
    return sum(notas) / len(notas)

def abrir_aba_notas(janela_pai, nome_usuario):
    notas_win = tk.Toplevel(janela_pai)
    notas_win.title("Notas")
    notas_win.geometry("600x400")

    notebook = ttk.Notebook(notas_win)
    notebook.pack(expand=True, fill='both')

    for materia in MATERIAS:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=materia)

        notas = pegar_notas_por_materia(nome_usuario, materia)
        if notas:
            tree = ttk.Treeview(frame, columns=('Questionário', 'Nota'), show='headings')
            tree.heading('Questionário', text='Questionário')
            tree.heading('Nota', text='Nota')
            tree.pack(expand=True, fill='both', pady=10, padx=10)

            notas_lista = []
            for nome_q, nota in notas:
                tree.insert('', 'end', values=(nome_q, f"{nota:.2f}"))
                notas_lista.append(nota)

            media = calcular_media(notas_lista)
            lbl_media = tk.Label(frame, text=f"Média: {media:.2f}", font=('Arial', 14))
            lbl_media.pack(pady=10)
        else:
            lbl_sem_notas = tk.Label(frame, text="Nenhuma nota registrada para essa matéria.", font=('Arial', 12))
            lbl_sem_notas.pack(pady=20)

