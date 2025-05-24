import sqlite3
import random

def conectar():
    return sqlite3.connect("banco.db")

def inicializador_do_banco():
    with conectar() as conexao:
        cursor = conexao.cursor()

        # Tabela usuario
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                idade INTEGER NOT NULL,
                estado TEXT NOT NULL
            )
        ''')

        # Tabela cursos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cursos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                conteudo TEXT NOT NULL
            )
        ''')

        # Tabela aulas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aulas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                curso_id INTEGER NOT NULL,
                titulo TEXT NOT NULL,
                video TEXT NOT NULL,
                FOREIGN KEY (curso_id) REFERENCES cursos(id)
            )
        ''')

        # Tabela questionarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questionarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aula_id INTEGER NOT NULL,
                titulo TEXT NOT NULL,
                materia TEXT,
                FOREIGN KEY (aula_id) REFERENCES aulas(id)
            )
        ''')

        # Tabela perguntas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS perguntas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                questionario_id INTEGER NOT NULL,
                texto TEXT NOT NULL,
                FOREIGN KEY (questionario_id) REFERENCES questionarios(id)
            )
        ''')

        # Tabela respostas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS respostas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pergunta_id INTEGER NOT NULL,
                texto TEXT NOT NULL,
                correta BOOLEAN NOT NULL,
                letra TEXT NOT NULL,
                FOREIGN KEY (pergunta_id) REFERENCES perguntas(id)
            )
        ''')

        # Tabela respostas_usuario
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS respostas_usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                pergunta_id INTEGER NOT NULL,
                resposta_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuario(id),
                FOREIGN KEY (pergunta_id) REFERENCES perguntas(id),
                FOREIGN KEY (resposta_id) REFERENCES respostas(id)
            )
        ''')

        # Tabela nota
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nota (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                id_questionario INTEGER NOT NULL,
                nota REAL NOT NULL,
                FOREIGN KEY (id_usuario) REFERENCES usuario(id),
                FOREIGN KEY (id_questionario) REFERENCES questionarios(id)
            )
        ''')

        # Inserir cursos se não existirem
        cursor.execute("SELECT COUNT(*) FROM cursos")
        total = cursor.fetchone()[0]

        if total == 0:
            cursos = [
                ("Matemática", "Aprenda conceitos fundamentais de Matemática, incluindo álgebra, geometria e estatística."),
                ("Tecnologia da Informação", "Entenda os fundamentos da TI, redes, hardware e software."),
                ("Infraestrutura Computacional", "Estude servidores, data centers e arquiteturas de rede."),
                ("Lei Geral de Proteção de Dados", "Conheça os princípios e regras da LGPD para proteger dados pessoais."),
                ("Cybersegurança", "Aprenda a proteger sistemas contra ameaças, ataques e vulnerabilidades.")
            ]
            cursor.executemany("INSERT INTO cursos (titulo, conteudo) VALUES (?, ?)", cursos)
            conexao.commit()

        # Inserir aulas se não existirem
        cursor.execute("SELECT COUNT(*) FROM aulas")
        total_aulas = cursor.fetchone()[0]

        if total_aulas == 0:
            aulas = [
                (1, "Aula 1 - Álgebra Básica", "https://www.youtube.com/watch?v=g1itgcYTXT8"),
                (1, "Aula 2 - Geometria", "https://www.youtube.com/watch?v=th5k6bzSDTA"),
                (1, "Aula 3 - Estatística","https://www.youtube.com/watch?v=mSk2vjGXA90"),
                (2, "Aula 1 - Fundamentos de TI", "https://www.youtube.com/watch?v=WULwZ6v_Ai8"),
                (2, "Aula 2 - Redes", "https://www.youtube.com/watch?v=q0S75nKpmcw"),
                (3, "Aula 1 - Conceitos básicos de infraestrutura", "https://www.youtube.com/watch?v=AvF8Gnft78k&list=PL866_LrQxNVhjUCo5b9iQLvgTtC9RoyO1"),
                (3, "Aula 2 - Componentes de infraestrutura",  "https://www.youtube.com/watch?v=j7k-nDkJVuA"),
                (3, "Aula 3 - Importância para negócios e sistemas", "https://www.youtube.com/watch?v=hvrrH-h96RM"),
                (4, "Aula 1 - Introdução à LGPD",  "https://www.youtube.com/watch?v=M-ETuNbmJN4"),
                (4, "Aula 2 - Direitos dos titulares", "https://www.youtube.com/watch?v=Wto-fwPnl8M"),
                (4, "Aula 3 - Responsabilidades dos controladores",  "https://www.youtube.com/watch?v=ZL-2DeBQxQ8"),
                (5, "Aula 1 - Introdução à Cybersegurança",  "https://www.youtube.com/watch?v=ZBK_wjexxZo"),
                (5, "Aula 2 - Tipos de ameaças",  "https://www.youtube.com/watch?v=1trXKqlA_e0"),
                (5, "Aula 3 - Como se proteger de cyber ataques", "https://www.youtube.com/watch?v=4teNCMcPabc"),
            ]
            cursor.executemany("INSERT INTO aulas (curso_id, titulo, video) VALUES (?, ?, ?)", aulas)
            conexao.commit()

        # Criar questionário para cada aula (se ainda não existir)
        cursor.execute("SELECT aulas.id, cursos.titulo FROM aulas JOIN cursos ON aulas.curso_id = cursos.id")
        aulas_com_curso = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM questionarios")
        total_questionarios = cursor.fetchone()[0]

        if total_questionarios == 0:
            for aula_id, curso_titulo in aulas_com_curso:
                titulo_questionario = f"Questionário da Aula {aula_id}"
                materia = None
                if "Matemática" in curso_titulo:
                    materia = "Matemática e Estatística"
                elif "Tecnologia da Informação" in curso_titulo:
                    materia = "Tecnologia da Informação"
                elif "Infraestrutura" in curso_titulo:
                    materia = "Infraestrutura Computacional"
                elif "LGPD" in curso_titulo:
                    materia = "Lei Geral de Proteção de Dados"
                elif "Cybersegurança" in curso_titulo or "Cyber" in curso_titulo:
                    materia = "Cyber Segurança"
                else:
                    materia = curso_titulo

                cursor.execute(
                    "INSERT INTO questionarios (aula_id, titulo, materia) VALUES (?, ?, ?)",
                    (aula_id, titulo_questionario, materia)
                )
            conexao.commit()

        # Pegar os ids dos questionários
        cursor.execute("SELECT id FROM questionarios")
        questionario_ids = [row[0] for row in cursor.fetchall()]

        # Inserir perguntas e respostas para cada questionário (se não existirem)
        cursor.execute("SELECT COUNT(*) FROM perguntas")
        total_perguntas = cursor.fetchone()[0]

        if total_perguntas == 0:
            for questionario_id in questionario_ids:
                for i in range(1, 8):
                    texto_pergunta = f"Pergunta {i}: Qual a resposta correta para a questão {i}?"
                    cursor.execute("INSERT INTO perguntas (questionario_id, texto) VALUES (?, ?)", (questionario_id, texto_pergunta))
                    conexao.commit()
                    pergunta_id = cursor.lastrowid

                    opcoes = [
                        f"Resposta A da pergunta {i}",
                        f"Resposta B da pergunta {i}",
                        f"Resposta C da pergunta {i}",
                    ]

                    indices = [0, 1, 2]
                    random.shuffle(indices)
                    correta_idx = indices[0]

                    letras = ['A', 'B', 'C']
                    respostas = []

                    for pos, idx_opcao in enumerate(indices):
                        texto_resposta = opcoes[idx_opcao]
                        correta = (pos == 0)
                        letra_alternativa = letras[pos]
                        respostas.append((pergunta_id, texto_resposta, correta, letra_alternativa))

                    cursor.executemany('''
                        INSERT INTO respostas (pergunta_id, texto, correta, letra)
                        VALUES (?, ?, ?, ?)
                    ''', respostas)
                    conexao.commit()

# Função para salvar a resposta do usuário
def salvar_resposta_usuario(usuario_id, pergunta_id, resposta_id):
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute('''
            INSERT INTO respostas_usuario (usuario_id, pergunta_id, resposta_id)
            VALUES (?, ?, ?)
        ''', (usuario_id, pergunta_id, resposta_id))
        conexao.commit()

# Função para salvar nota do questionário para usuário
def salvar_nota_usuario(id_usuario, id_questionario, nota):
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute('''
            SELECT id FROM nota WHERE id_usuario = ? AND id_questionario = ?
        ''', (id_usuario, id_questionario))
        resultado = cursor.fetchone()
        if resultado:
            cursor.execute('''
                UPDATE nota SET nota = ? WHERE id = ?
            ''', (nota, resultado[0]))
        else:
            cursor.execute('''
                INSERT INTO nota (id_usuario, id_questionario, nota) VALUES (?, ?, ?)
            ''', (id_usuario, id_questionario, nota))
        conexao.commit()

# NOVAS FUNÇÕES: buscar notas e média do usuário

def buscar_notas_usuario(id_usuario):
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute('''
            SELECT q.titulo, n.nota 
            FROM nota n
            JOIN questionarios q ON n.id_questionario = q.id
            WHERE n.id_usuario = ?
        ''', (id_usuario,))
        return cursor.fetchall()

def calcular_media_geral(id_usuario):
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute('''
            SELECT AVG(nota)
            FROM nota
            WHERE id_usuario = ?
        ''', (id_usuario,))
        media = cursor.fetchone()[0]
        return media if media is not None else 0.0

if __name__ == "__main__":
    inicializador_do_banco()
