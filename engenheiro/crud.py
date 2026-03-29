import sqlite3
import uuid

DB_NAME = "engenheiros.db"


def conectar():
    return sqlite3.connect(DB_NAME)


def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS engenheiros (
        id TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        idade INTEGER,
        especialidade TEXT
    )
    """)

    conn.commit()
    conn.close()


def criar_engenheiro(nome, idade=None, especialidade=None):
    conn = conectar()
    cursor = conn.cursor()

    id = str(uuid.uuid4())

    cursor.execute("""
    INSERT INTO engenheiros (id, nome, idade, especialidade)
    VALUES (?, ?, ?, ?)
    """, (id, nome, idade, especialidade))

    conn.commit()
    conn.close()

    return id


def listar_engenheiros():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM engenheiros")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("\nNenhum engenheiro cadastrado.\n")
        return

    for row in rows:
        print(f"""
ID: {row[0]}
Nome: {row[1]}
Idade: {row[2]}
Especialidade: {row[3]}
---------------------------""")


def ler_engenheiro(id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM engenheiros WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        print(f"""
ID: {row[0]}
Nome: {row[1]}
Idade: {row[2]}
Especialidade: {row[3]}
""")
    else:
        print("Engenheiro não encontrado.\n")


def atualizar_engenheiro(id, nome=None, idade=None, especialidade=None):
    conn = conectar()
    cursor = conn.cursor()

    campos = []
    valores = []

    if nome:
        campos.append("nome = ?")
        valores.append(nome)

    if idade is not None:
        campos.append("idade = ?")
        valores.append(idade)

    if especialidade:
        campos.append("especialidade = ?")
        valores.append(especialidade)

    if not campos:
        print("Nada para atualizar.\n")
        return

    valores.append(id)

    query = f"UPDATE engenheiros SET {', '.join(campos)} WHERE id = ?"
    cursor.execute(query, valores)

    conn.commit()
    conn.close()

    print("Atualizado com sucesso.\n")


def deletar_engenheiro(id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM engenheiros WHERE id = ?", (id,))
    conn.commit()

    if cursor.rowcount > 0:
        print("Deletado com sucesso.\n")
    else:
        print("Engenheiro não encontrado.\n")

    conn.close()


# ----------------------
# INTERFACE INTERATIVA
# ----------------------

def menu():
    print("""
==== CRUD ENGENHEIROS ====

1 - Criar engenheiro
2 - Listar engenheiros
3 - Ler engenheiro
4 - Atualizar engenheiro
5 - Deletar engenheiro
0 - Sair

Escolha uma opção:
""")


def input_opcional_int(texto):
    valor = input(texto).strip()
    if valor == "":
        return None
    try:
        return int(valor)
    except:
        print("Valor inválido. Ignorando campo.")
        return None


def main():
    criar_tabela()

    while True:
        menu()
        opcao = input("> ").strip()

        if opcao == "1":
            nome = input("Nome: ").strip()

            if not nome:
                print("Nome é obrigatório.\n")
                continue

            idade = input_opcional_int("Idade (opcional): ")
            especialidade = input("Especialidade (opcional): ").strip() or None

            id = criar_engenheiro(nome, idade, especialidade)
            print(f"Criado com ID: {id}\n")

        elif opcao == "2":
            listar_engenheiros()

        elif opcao == "3":
            id = input("ID: ").strip()
            ler_engenheiro(id)

        elif opcao == "4":
            id = input("ID: ").strip()

            print("Deixe em branco para não alterar.")
            nome = input("Novo nome: ").strip() or None
            idade = input_opcional_int("Nova idade: ")
            especialidade = input("Nova especialidade: ").strip() or None

            atualizar_engenheiro(id, nome, idade, especialidade)

        elif opcao == "5":
            id = input("ID: ").strip()
            deletar_engenheiro(id)

        elif opcao == "0":
            print("Saindo...")
            break

        else:
            print("Opção inválida.\n")


if __name__ == "__main__":
    main()
