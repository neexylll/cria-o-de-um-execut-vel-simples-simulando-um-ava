def on_enter(event):
    event.widget['background'] = '#444444'
    event.widget['foreground'] = 'white'

def on_leave(event):
    event.widget['background'] = 'black'
    event.widget['foreground'] = 'white'

def aplicar_hover(botao):
    botao.bind("<Enter>", on_enter)
    botao.bind("<Leave>", on_leave)
