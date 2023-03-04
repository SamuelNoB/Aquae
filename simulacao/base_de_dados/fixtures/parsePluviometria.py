import json

# Lê o arquivo JSON
with open('../Pluviometria_fixture.json', 'r') as f:
    data = json.load(f)

# Separa o conteúdo em lotes de até 200 registros
lote = 1
while len(data) > 0:
    # Define o nome do arquivo
    nome_arquivo = f'Pluviometria_fixture-{lote:02d}.json'
    
    # Pega os primeiros 200 registros e remove-os da lista original
    registros = data[:100]
    data = data[100:]
    
    # Salva os registros em um novo arquivo JSON
    with open(nome_arquivo, 'w') as f:
        json.dump(registros, f, separators=(',', ':'), ensure_ascii=False, indent=None)
    
    # Incrementa o número do lote
    lote += 1