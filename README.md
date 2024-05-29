# Interface CRUD com Tkinter e MySQL

Este projeto é uma aplicação de interface gráfica (GUI) desenvolvida com Tkinter que permite operações CRUD (Criar, Ler, Atualizar, Excluir) em um banco de dados MySQL.

## Funcionalidades

- **Conexão com Banco de Dados MySQL:** Conecta-se ao banco de dados especificado e permite operações CRUD nas tabelas.
- **CRUD em Tabelas Existentes:** Interface para criar novos registros, ler registros existentes, atualizar registros e excluir registros de tabelas existentes.
- **Criação de Novas Tabelas:** Interface para criar novas tabelas no banco de dados.
- **Logging de Erros:** Registra erros em um arquivo de log (`app.log`).

## Dependências

- `mysql-connector-python`: Biblioteca para conexão com MySQL.
- `tkinter`: Biblioteca padrão do Python para interfaces gráficas.
- `logging`: Biblioteca padrão do Python para logging.

## Instalação

1. **Clone o repositório:**
    ```sh
    git clone <url-do-repositorio>
    cd <nome-do-repositorio>
    ```

2. **Crie um ambiente virtual:**
    ```sh
    python -m venv venv
    ```

3. **Ative o ambiente virtual:**

    - No Windows:
        ```sh
        venv\Scripts\activate
        ```
    - No Linux/MacOS:
        ```sh
        source venv/bin/activate
        ```

4. **Instale as dependências:**
    ```sh
    pip install -r requirements.txt
    ```

## Configuração

Antes de executar a aplicação, certifique-se de configurar as informações de conexão com o banco de dados MySQL no arquivo principal do projeto.

```python
self.con = connect(
    user='seu_usuario',
    password='sua_senha',
    host='localhost',
    port='3306',
    database='seu_banco_de_dados',
)
