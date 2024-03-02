import tabula

# Caminho para o arquivo PDF
caminho_pdf = "fatura.pdf"

# Extrair tabelas do PDF
tabelas = tabula.read_pdf(caminho_pdf, pages="all", multiple_tables=True)

# Iterar sobre as tabelas extraídas
for i, tabela in enumerate(tabelas):
    print(f"Tabela {i + 1}:")
    print(tabela)
    print("\n")