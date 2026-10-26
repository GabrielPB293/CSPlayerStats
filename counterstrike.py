import csv
import os

# O arquivo CSV deve ficar na mesma pasta deste programa.
PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO = os.path.join(PASTA, "Counter Strike all Time best Players Stats.csv")

# Faixas usadas para agrupar os jogadores pela nota do jogador.
FAIXAS = [
    ("Abaixo de 0.90", 0.0, 0.90),
    ("0.90 a 0.94", 0.90, 0.95),
    ("0.95 a 0.99", 0.95, 1.00),
    ("1.00 a 1.04", 1.00, 1.05),
    ("1.05 a 1.09", 1.05, 1.10),
    ("1.10 ou mais", 1.10, 99.0),
]

# Criterios usados na analise com conjuntos.
CRITERIOS = {
    "1": ("K/D acima de 1.10", lambda jogador: jogador["K/D"] > 1.10),
    "2": ("nota do jogador de 1.05 ou mais", lambda jogador: jogador["Rating 1.0"] >= 1.05),
    "3": ("1000 mapas ou mais", lambda jogador: jogador["Maps"] >= 1000),
    "4": ("K-D Diff positivo", lambda jogador: jogador["K-D Diff"] > 0),
    "5": ("nota do jogador abaixo de 1.00", lambda jogador: jogador["Rating 1.0"] < 1.00),
}


def carregar_jogadores():
    """Lê o CSV e guarda os dados em uma lista de dicionários."""
    jogadores = []

    with open(ARQUIVO, mode="r", encoding="utf-8-sig", newline="") as arquivo:
        dados_csv = csv.DictReader(arquivo)

        # Remove o espaco invisivel que existe no cabecalho K-D Diff do CSV.
        dados_csv.fieldnames = [
            nome.replace("\xa0", " ").strip()
            for nome in dados_csv.fieldnames
        ]

        for linha in dados_csv:
            jogador = {
                "Player": linha["Player"].strip(),
                "Maps": int(linha["Maps"]),
                "Rounds": int(linha["Rounds"]),
                "K-D Diff": int(linha["K-D Diff"]),
                "K/D": float(linha["K/D"]),
                "Rating 1.0": float(linha["Rating 1.0"]),
            }
            jogadores.append(jogador)

    return jogadores


def titulo(texto):
    print()
    print(texto)
    print("-" * 55)


def mostrar_tabela(cabecalhos, linhas):
    """Desenha uma tabela com bordas e colunas alinhadas."""
    larguras = []
    for coluna, cabecalho in enumerate(cabecalhos):
        maior = len(str(cabecalho))
        for linha in linhas:
            maior = max(maior, len(str(linha[coluna])))
        larguras.append(maior + 2)

    separador = "+"
    for largura in larguras:
        separador += "-" * largura + "+"

    def mostrar_linha(valores):
        texto = "|"
        for valor, largura in zip(valores, larguras):
            texto += f"{str(valor):^{largura}}|"
        print(texto)

    print(separador)
    mostrar_linha(cabecalhos)
    print(separador)
    for linha in linhas:
        mostrar_linha(linha)
    print(separador)


def agrupar_por_rating(jogadores):
    """Agrupa em um dicionario e mostra as faixas mais populosas primeiro."""
    titulo("Quantidade de jogadores em cada faixa de nota")
    grupos = {}

    for nome, minimo, maximo in FAIXAS:
        grupos[nome] = []

    for jogador in jogadores:
        for nome, minimo, maximo in FAIXAS:
            if minimo <= jogador["Rating 1.0"] < maximo:
                grupos[nome].append(jogador)
                break

    grupos_ordenados = sorted(grupos.items(), key=lambda grupo: len(grupo[1]), reverse=True)
    linhas = []
    for nome, lista in grupos_ordenados:
        linhas.append([nome, len(lista)])
    mostrar_tabela(["Faixa da nota", "Quantidade de jogadores"], linhas)


def listar_top_jogadores(jogadores):
    """Ordena a lista pelo atributo escolhido e mostra os primeiros jogadores."""
    titulo("Top jogadores por atributo")
    atributos = {
        "1": ("Maps", "Quantidade de mapas"),
        "2": ("Rounds", "Quantidade de rounds"),
        "3": ("K-D Diff", "Diferença entre eliminações e mortes"),
        "4": ("K/D", "K/D (eliminações por morte)"),
        "5": ("Rating 1.0", "Nota do jogador"),
    }

    print("1. Maps (quantidade de mapas)")
    print("2. Rounds (quantidade de rounds)")
    print("3. K-D Diff (diferença entre eliminações e mortes)")
    print("4. K/D (eliminações por morte)")
    print("5. Nota do jogador")
    opcao = input("Digite o número do atributo que deseja ordenar: ").strip()

    if opcao not in atributos:
        print("Opção inválida. Escolha um atributo de 1 a 5.")
        return

    atributo, nome_atributo = atributos[opcao]
    try:
        quantidade = int(input("Quantos jogadores deseja listar? (exemplo: 10 ou 20): "))
        if quantidade <= 0:
            quantidade = 10
    except ValueError:
        quantidade = 10

    jogadores_ordenados = sorted(jogadores, key=lambda jogador: jogador[atributo], reverse=True)
    linhas = []
    for posicao, jogador in enumerate(jogadores_ordenados[:quantidade], start=1):
        valor = jogador[atributo]
        if isinstance(valor, float):
            valor = f"{valor:.2f}"
        linhas.append([posicao, jogador["Player"], valor])
    mostrar_tabela(["Posição", "Nome do jogador", nome_atributo], linhas)


def comparar_faixas(jogadores):
    """Compara a quantidade, a soma e a média de um atributo entre faixas."""
    titulo("Comparação de estatísticas entre faixas de nota")
    grupos = {}

    for nome, minimo, maximo in FAIXAS:
        grupos[nome] = []

    for jogador in jogadores:
        for nome, minimo, maximo in FAIXAS:
            if minimo <= jogador["Rating 1.0"] < maximo:
                grupos[nome].append(jogador)
                break

    for numero, (nome, minimo, maximo) in enumerate(FAIXAS, start=1):
        print(f"{numero}. Faixa {nome}")

    entrada = input("Digite os números de duas ou mais faixas, separados por vírgula (exemplo: 1, 3, 6): ")
    escolhidas = []
    for parte in entrada.split(","):
        parte = parte.strip()
        if parte.isdigit() and 1 <= int(parte) <= len(FAIXAS):
            nome = FAIXAS[int(parte) - 1][0]
            if nome not in escolhidas:
                escolhidas.append(nome)

    if len(escolhidas) < 2:
        print("Escolha pelo menos duas faixas válidas para comparar.")
        return

    print("\nQual estatística deseja comparar?")
    print("1. Maps (quantidade de mapas)")
    print("2. Rounds (quantidade de rounds)")
    print("3. K-D Diff (diferença entre eliminações e mortes)")
    print("4. K/D (eliminações por morte)")
    print("5. Nota do jogador")
    atributos = {"1": "Maps", "2": "Rounds", "3": "K-D Diff", "4": "K/D", "5": "Rating 1.0"}
    opcao = input("Digite o número da estatística: ").strip()

    if opcao not in atributos:
        print("Opção inválida. Escolha uma estatística de 1 a 5.")
        return

    atributo = atributos[opcao]
    nome_atributo = {
        "Maps": "mapas",
        "Rounds": "Rounds",
        "K-D Diff": "K-D Diff",
        "K/D": "K/D",
        "Rating 1.0": "nota do jogador",
    }[atributo]
    print(f"\nSoma e média calculadas para: {nome_atributo}")
    linhas = []

    for nome in escolhidas:
        valores = [jogador[atributo] for jogador in grupos[nome]]
        soma = sum(valores)
        media = soma / len(valores) if valores else 0
        linhas.append([nome, len(valores), f"{soma:.2f}", f"{media:.2f}"])

    mostrar_tabela(
        ["Faixa da nota", "Quantidade de jogadores", f"Soma de {nome_atributo}", f"Média de {nome_atributo}"],
        linhas,
    )


def analisar_conjuntos(jogadores):
    """Calcula união, interseção e diferenças entre dois conjuntos de jogadores."""
    titulo("Operações com conjuntos de jogadores")

    for chave, (descricao, teste) in CRITERIOS.items():
        print(f"{chave}. Selecionar jogadores com {descricao}")

    opcao_a = input("Digite o número do primeiro critério (conjunto A): ").strip()
    opcao_b = input("Digite o número do segundo critério (conjunto B): ").strip()

    if opcao_a not in CRITERIOS or opcao_b not in CRITERIOS or opcao_a == opcao_b:
        print("Escolha dois critérios válidos e diferentes para formar os conjuntos A e B.")
        return

    descricao_a, teste_a = CRITERIOS[opcao_a]
    descricao_b, teste_b = CRITERIOS[opcao_b]
    conjunto_a = set()
    conjunto_b = set()

    for jogador in jogadores:
        if teste_a(jogador):
            conjunto_a.add(jogador["Player"])
        if teste_b(jogador):
            conjunto_b.add(jogador["Player"])

    print(f"\nA = {descricao_a} ({len(conjunto_a)} jogadores)")
    print(f"B = {descricao_b} ({len(conjunto_b)} jogadores)")
    mostrar_conjunto("União: jogadores que atendem a A ou B", conjunto_a | conjunto_b)
    mostrar_conjunto("Interseção: jogadores que atendem a A e B", conjunto_a & conjunto_b)
    mostrar_conjunto("Diferença A - B: jogadores que atendem somente a A", conjunto_a - conjunto_b)
    mostrar_conjunto("Diferença B - A: jogadores que atendem somente a B", conjunto_b - conjunto_a)


def mostrar_conjunto(texto, conjunto):
    nomes = sorted(list(conjunto), key=str.lower)
    print(f"\n{texto} ({len(nomes)} jogadores):")
    print(", ".join(nomes) if nomes else "Nenhum jogador atende a esta operação.")


def tabela_top10_rating(jogadores):
    """Mostra uma tabela com os dez jogadores de maior nota."""
    titulo("Dez jogadores com as maiores notas")
    jogadores_ordenados = sorted(jogadores, key=lambda jogador: jogador["Rating 1.0"], reverse=True)

    linhas = []
    for posicao, jogador in enumerate(jogadores_ordenados[:10], start=1):
        linhas.append([posicao, jogador["Player"], f"{jogador['Rating 1.0']:.2f}"])
    mostrar_tabela(["Posição", "Nome do jogador", "Nota do jogador"], linhas)


def tabela_kd_rating(jogadores):
    """Mostra em tabela o K/D e a nota de cada jogador."""
    titulo("K/D (eliminações por morte) e nota de todos os jogadores")
    jogadores_ordenados = sorted(jogadores, key=lambda jogador: jogador["Rating 1.0"], reverse=True)
    top5 = set()

    for jogador in jogadores_ordenados[:5]:
        top5.add(jogador["Player"])

    print("* marca os cinco jogadores com as maiores notas.")
    linhas = []
    for jogador in jogadores_ordenados:
        destaque = "*" if jogador["Player"] in top5 else " "
        linhas.append([destaque, jogador["Player"], f"{jogador['K/D']:.2f}", f"{jogador['Rating 1.0']:.2f}"])
    mostrar_tabela(["Destaque", "Nome do jogador", "K/D", "Nota do jogador"], linhas)


def menu():
    if not os.path.exists(ARQUIVO):
        print(f"Arquivo CSV não encontrado: {ARQUIVO}")
        print("Coloque o arquivo CSV na mesma pasta deste programa e tente novamente.")
        return

    jogadores = carregar_jogadores()
    print(f"Foram carregados {len(jogadores)} jogadores do arquivo CSV.")

    while True:
        titulo("Counter-Strike: análise das estatísticas dos jogadores")
        print("1. Agrupar jogadores por faixa da nota e contar cada grupo")
        print("2. Ordenar jogadores e listar os maiores valores de uma estatística")
        print("3. Comparar quantidade, soma e média de uma estatística entre faixas")
        print("4. Comparar grupos de jogadores usando união, interseção e diferença")
        print("5. Exibir tabela dos dez jogadores com as maiores notas")
        print("6. Exibir tabela de K/D e nota para todos os jogadores")
        print("7. Encerrar o programa")

        opcao = input("Digite o número da opção desejada: ").strip()
        if opcao == "1":
            agrupar_por_rating(jogadores)
        elif opcao == "2":
            listar_top_jogadores(jogadores)
        elif opcao == "3":
            comparar_faixas(jogadores)
        elif opcao == "4":
            analisar_conjuntos(jogadores)
        elif opcao == "5":
            tabela_top10_rating(jogadores)
        elif opcao == "6":
            tabela_kd_rating(jogadores)
        elif opcao == "7":
            print("Programa encerrado. Até mais!")
            break
        else:
            print("Opção inválida. Digite um número de 1 a 7.")


if __name__ == "__main__":
    menu()
