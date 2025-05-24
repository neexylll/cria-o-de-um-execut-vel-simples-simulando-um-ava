import tkinter as tk
from tkinter import messagebox

# Variável global para o timer
timer_id = None
TIMEOUT = 3600 * 1000  # 1 hora em ms

def encerrar_por_inatividade():
    messagebox.showinfo("Encerrando", "O programa será fechado por inatividade.")
    # Fecha todas as janelas abertas (termina a aplicação)
    for widget in tk._default_root.winfo_children():
        widget.destroy()
    tk._default_root.destroy()

def resetar_timer(event=None):
    global timer_id
    if timer_id is not None:
        tk._default_root.after_cancel(timer_id)
    timer_id = tk._default_root.after(TIMEOUT, encerrar_por_inatividade)

def iniciar_monitoramento_inatividade(janela):
    # Vincula eventos a TODAS as janelas e widgets para resetar o timer
    janela.bind_all("<Any-KeyPress>", resetar_timer)
    janela.bind_all("<Any-Button>", resetar_timer)
    janela.bind_all("<Motion>", resetar_timer)

    resetar_timer()

# Exemplo de uso na janela principal:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("App Principal")
    root.geometry("300x200")

    iniciar_monitoramento_inatividade(root)

    lbl = tk.Label(root, text="App aberto. Ele fechará em 1 hora sem atividade.")
    lbl.pack(pady=50)

    root.mainloop()
