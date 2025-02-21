# Caixa-Imoveis-Automation

# Automacao de Imoveis

Este projeto automatiza o download, tratamento e inserção de dados de imóveis no banco de dados a partir do site da Caixa.

## Funcionalidades

- **Download Automático**: Baixa listas de imóveis por estado diretamente do site da Caixa.
- **Unificação de Dados**: Mescla arquivos CSV de diferentes estados em um só.
- **Integração com Banco de Dados**: Insere novos dados e remove registros que não estão mais na planilha.
- **Organização dos Arquivos**: Garante que os arquivos de planilha sejam armazenados corretamente.

## Tecnologias Utilizadas

- **Python**
  - `selenium` para automação do navegador
  - `pandas` para manipulação de dados
  - `mysql.connector` para interação com o banco de dados
  - `shutil` e `os` para manipulação de arquivos e diretórios

## Como Usar

### 1. Instale as Dependências

Certifique-se de ter o Python instalado e execute o seguinte comando para instalar as bibliotecas necessárias:

```sh
pip install selenium pandas mysql-connector-python
```

### 2. Configurar Variáveis de Ambiente

Antes de rodar o script, configure as variáveis de ambiente para o banco de dados:

```sh
set DB_HOST=seu_host
set DB_USER=seu_usuario
set DB_PASSWORD=sua_senha
set DB_DATABASE=seu_banco
set DB_PORT=sua_porta
```

Ou crie um arquivo `.env` com o seguinte conteúdo:

```
DB_HOST=seu_host
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_DATABASE=seu_banco
DB_PORT=sua_porta
```

### 3. Executar o Script

```sh
python script.py
```

O script irá:

1. Criar a pasta `planilhas` caso não exista.
2. Baixar os arquivos CSV do site da Caixa.
3. Unificar os arquivos em uma planilha principal.
4. Conectar-se ao banco de dados.
5. Remover registros do banco que não estão mais na planilha.
6. Inserir novos dados no banco.

### 4. Limpeza de Arquivos

Após a execução, a pasta `planilhas/` será removida automaticamente para manter o diretório organizado.


