# Interface CRUD com Tkinter e MySQL

Este é um programa que oferece uma interface gráfica para realizar operações CRUD (Create, Read, Update, Delete) em um banco de dados MySQL. Ele foi desenvolvido utilizando a biblioteca Tkinter para a interface gráfica e MySQL Connector para se comunicar com o banco de dados MySQL.

## Funcionalidades

- **Criar**: Permite criar uma nova tabela no banco de dados, especificando o nome da tabela e suas colunas.
- **Ler**: Permite visualizar os registros de uma tabela existente, selecionando a tabela desejada e exibindo os dados em uma interface de tabela.
- **Atualizar**: Possibilita atualizar os registros de uma tabela existente, fornecendo o ID do registro a ser atualizado e os novos valores para suas colunas.
- **Excluir**: Permite excluir registros de uma tabela existente, fornecendo o ID do registro a ser excluído.
- **Importar/Exportar**: Oferece a capacidade de importar e exportar dados de tabelas no formato SQL.
- **Editor SQL**: Permite executar comandos SQL personalizados e visualizar os resultados.

## Requisitos

- Python 3.x
- MySQL Server
- MySQL Connector Python
- Tkinter
- ttkthemes

## Como usar

1. Certifique-se de ter instalado todas as dependências listadas nos requisitos.
2. Execute o programa `interface_crud.py`.
3. A interface gráfica será aberta, permitindo que você execute as operações CRUD e utilize o editor SQL.

## Estrutura do Código

- `interface_crud.py`: Contém o código-fonte principal do programa, que define a interface gráfica e suas funcionalidades.
- `conectar_db.py`: Classe responsável por lidar com a conexão com o banco de dados e as operações CRUD.
- `app.log`: Arquivo de log para registrar erros durante a execução do programa.

## Contribuindo

Contribuições são bem-vindas! Se você encontrar algum problema, bug ou tiver ideias para melhorias, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Licença

Este projeto está licenciado sob a Licença MIT. Consulte o arquivo LICENSE para obter mais detalhes.
