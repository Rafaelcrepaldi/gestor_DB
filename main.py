import tkinter as tk
from tkinter import ttk, messagebox
from mysql.connector import connect, Error
import logging

# Configuração do logging
logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class ConectarDB:
    def __init__(self):
        try:
            self.con = connect(
                user='aps1',
                password='1234',
                host='localhost',
                port='3306',
                database='aps1',
            )
            self.cur = self.con.cursor()
        except Error as e:
            logging.error(f"Erro de Conexão: {e}")
            messagebox.showerror("Erro de Conexão", f"Falha ao conectar ao banco de dados: {e}")

    def inserir_linha(self, tabela, dados):
        colunas = ', '.join(dados.keys())
        valores = ', '.join(['%s'] * len(dados))
        query = f'''INSERT INTO {tabela} ({colunas}) VALUES ({valores});'''
        try:
            self.cur.execute(query, tuple(dados.values()))
        except Error as e:
            self.con.rollback()
            logging.error(f"Erro de Inserção: {e}")
        else:
            self.con.commit()
            logging.info("Registro inserido com sucesso")

    def encontrar_linhas(self, tabela):
        query = f'SELECT * FROM {tabela};'
        self.cur.execute(query)
        return self.cur.fetchall()

    def encontrar_linha_por_id(self, tabela, rowid):
        query = f'SELECT * FROM {tabela} WHERE id = %s;'
        self.cur.execute(query, (rowid,))
        return self.cur.fetchone()

    def obter_colunas(self, tabela):
        query = f'SHOW COLUMNS FROM {tabela};'
        self.cur.execute(query)
        return [coluna[0] for coluna in self.cur.fetchall()]

    def alterar_linha(self, tabela, rowid, dados):
        set_clause = ', '.join([f"{col} = %s" for col in dados.keys()])
        query = f'''UPDATE {tabela} SET {set_clause} WHERE id = %s;'''
        try:
            self.cur.execute(query, tuple(dados.values()) + (rowid,))
        except Error as e:
            self.con.rollback()
            logging.error(f"Erro de Atualização: {e}")
        else:
            self.con.commit()
            logging.info("Registro atualizado com sucesso")

    def remover_linha(self, tabela, rowid):
        query = f'DELETE FROM {tabela} WHERE id = %s;'
        try:
            self.cur.execute(query, (rowid,))
        except Error as e:
            self.con.rollback()
            logging.error(f"Erro de Remoção: {e}")
        else:
            self.con.commit()
            logging.info("Registro removido com sucesso")

    def remover_linha_por_numero(self, tabela, numero_linha):
        query = f'SELECT id FROM {tabela} LIMIT %s, 1;'
        self.cur.execute(query, (numero_linha - 1,))
        resultado = self.cur.fetchone()
        if resultado:
            self.remover_linha(tabela, resultado[0])

    def excluir_tabela(self, tabela):
        query = f'DROP TABLE {tabela};'
        try:
            self.cur.execute(query)
        except Error as e:
            self.con.rollback()
            logging.error(f"Erro ao Excluir Tabela: {e}")
        else:
            self.con.commit()
            logging.info("Tabela excluída com sucesso")

    def fechar(self):
        self.cur.close()
        self.con.close()

    def listar_tabelas(self):
        query = "SHOW TABLES;"
        try:
            self.cur.execute(query)
            tabelas = self.cur.fetchall()
            return [tabela[0] for tabela in tabelas]
        except Error as e:
            logging.error(f"Erro ao Listar Tabelas: {e}")
            messagebox.showerror("Erro ao Listar Tabelas", f"Falha ao listar tabelas: {e}")
            return []

class Aplicacao(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Interface CRUD")
        self.geometry("800x600")
        self.db = ConectarDB()

        self.criar_widgets()

    def criar_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, expand=True)

        self.frame1 = self.criar_frame("Criar")
        self.frame2 = self.criar_frame("Ler")
        self.frame3 = self.criar_frame("Atualizar")
        self.frame4 = self.criar_frame("Excluir")
        self.frame5 = self.criar_frame("Nova Tabela")

        self.tab_criar()
        self.tab_ler()
        self.tab_atualizar()
        self.tab_excluir()
        self.tab_nova_tabela()

    def criar_frame(self, titulo):
        frame = ttk.Frame(self.notebook, width=800, height=600)
        frame.pack(fill="both", expand=True)
        self.notebook.add(frame, text=titulo)
        return frame

    def tab_criar(self):
        ttk.Label(self.frame1, text="Selecione a Tabela:").grid(row=0, column=0, padx=10, pady=10)
        self.lista_tabelas_criar = tk.StringVar()
        self.dropdown_tabelas_criar = ttk.Combobox(self.frame1, textvariable=self.lista_tabelas_criar)
        self.dropdown_tabelas_criar.grid(row=0, column=1, padx=10, pady=10)
        self.dropdown_tabelas_criar['values'] = self.db.listar_tabelas()
        self.dropdown_tabelas_criar.bind("<<ComboboxSelected>>", self.atualizar_formulario_criar)

        self.entries_criar = []

    def atualizar_formulario_criar(self, event):
        for widget in self.frame1.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:
                widget.grid_forget()
                
        tabela = self.lista_tabelas_criar.get()
        colunas = self.db.obter_colunas(tabela)
        
        self.entries_criar = []
        for idx, coluna in enumerate(colunas):
            ttk.Label(self.frame1, text=f"{coluna}:").grid(row=idx + 1, column=0, padx=10, pady=10)
            entrada = ttk.Entry(self.frame1)
            entrada.grid(row=idx + 1, column=1, padx=10, pady=10)
            self.entries_criar.append((coluna, entrada))
        
        self.botao_criar = ttk.Button(self.frame1, text="Adicionar Registro", command=self.adicionar_registro)
        self.botao_criar.grid(row=len(colunas) + 1, column=0, columnspan=2, pady=10)

    def adicionar_registro(self):
        tabela = self.lista_tabelas_criar.get()
        dados = {coluna: entrada.get() for coluna, entrada in self.entries_criar}
        if tabela and all(dados.values()):
            self.db.inserir_linha(tabela, dados)
            messagebox.showinfo("Sucesso", "Registro adicionado com sucesso")
        else:
            messagebox.showwarning("Erro de Entrada", "Por favor, preencha todos os campos com dados válidos")

    def tab_ler(self):
        self.lista_tabelas = tk.StringVar()
        ttk.Label(self.frame2, text="Selecione a Tabela:").grid(row=0, column=0, padx=10, pady=10)
        self.dropdown_tabelas = ttk.Combobox(self.frame2, textvariable=self.lista_tabelas)
        self.dropdown_tabelas.grid(row=0, column=1, padx=10, pady=10)
        self.dropdown_tabelas['values'] = self.db.listar_tabelas()

        self.botao_ler = ttk.Button(self.frame2, text="Buscar Registros", command=self.buscar_registros)
        self.botao_ler.grid(row=1, column=0, columnspan=2, pady=10)

        self.tree = ttk.Treeview(self.frame2, show="headings")
        self.tree.grid(row=2, column=0, columnspan=2, pady=10)

        self.label_total_linhas = ttk.Label(self.frame2, text="Total de Linhas: 0")
        self.label_total_linhas.grid(row=3, column=0, columnspan=2, pady=10)

    def buscar_registros(self):
        nome_tabela = self.lista_tabelas.get()
        if not nome_tabela:
            messagebox.showwarning("Erro de Entrada", "Por favor, selecione uma tabela")
            return

        query = f"SELECT * FROM {nome_tabela};"
        try:
            self.db.cur.execute(query)
            colunas = [desc[0] for desc in self.db.cur.description]
            linhas = self.db.cur.fetchall()

            self.tree['columns'] = ["Número"] + colunas
            self.tree.delete(*self.tree.get_children())
            self.tree.heading("#0", text="")
            self.tree.column("#0", width=0, stretch=tk.NO)
            
            for i, coluna in enumerate(["Número"] + colunas):
                self.tree.heading(f"#{i}", text=coluna)
                self.tree.column(f"#{i}", anchor=tk.W)

            for i, linha in enumerate(linhas):
                self.tree.insert("", tk.END, text="", values=(i + 1, *linha))
            
            self.label_total_linhas['text'] = f"Total de Linhas: {len(linhas)}"
        except Error as e:
            logging.error(f"Erro ao Buscar Registros: {e}")
            messagebox.showerror("Erro ao Buscar Registros", f"Falha ao buscar registros: {e}")

    def tab_atualizar(self):
        ttk.Label(self.frame3, text="Selecione a Tabela:").grid(row=0, column=0, padx=10, pady=10)
        self.lista_tabelas_atualizar = tk.StringVar()
        self.dropdown_tabelas_atualizar = ttk.Combobox(self.frame3, textvariable=self.lista_tabelas_atualizar)
        self.dropdown_tabelas_atualizar.grid(row=0, column=1, padx=10, pady=10)
        self.dropdown_tabelas_atualizar['values'] = self.db.listar_tabelas()
        self.dropdown_tabelas_atualizar.bind("<<ComboboxSelected>>", self.atualizar_formulario_atualizar)

        ttk.Label(self.frame3, text="ID:").grid(row=1, column=0, padx=10, pady=10)
        self.entrada_id_atualizar = ttk.Entry(self.frame3)
        self.entrada_id_atualizar.grid(row=1, column=1, padx=10, pady=10)

        self.botao_buscar = ttk.Button(self.frame3, text="Buscar Registro", command=self.buscar_registro)
        self.botao_buscar.grid(row=2, column=0, columnspan=2, pady=10)

        self.entries_atualizar = []

    def atualizar_formulario_atualizar(self, event):
        for widget in self.frame3.grid_slaves():
            if int(widget.grid_info()["row"]) > 2:
                widget.grid_forget()

    def buscar_registro(self):
        tabela = self.lista_tabelas_atualizar.get()
        rowid = self.entrada_id_atualizar.get()
        if tabela and rowid.isdigit():
            registro = self.db.encontrar_linha_por_id(tabela, int(rowid))
            colunas = self.db.obter_colunas(tabela)

            if registro:
                self.entries_atualizar = []
                for idx, (coluna, valor) in enumerate(zip(colunas, registro)):
                    ttk.Label(self.frame3, text=f"{coluna}:").grid(row=idx + 3, column=0, padx=10, pady=10)
                    entrada = ttk.Entry(self.frame3)
                    entrada.grid(row=idx + 3, column=1, padx=10, pady=10)
                    entrada.insert(0, valor)
                    self.entries_atualizar.append((coluna, entrada))
                
                self.botao_atualizar = ttk.Button(self.frame3, text="Atualizar Registro", command=self.atualizar_registro)
                self.botao_atualizar.grid(row=len(colunas) + 3, column=0, columnspan=2, pady=10)
            else:
                messagebox.showwarning("Erro de Entrada", "Registro não encontrado")
        else:
            messagebox.showwarning("Erro de Entrada", "Por favor, insira um ID válido")

    def atualizar_registro(self):
        tabela = self.lista_tabelas_atualizar.get()
        rowid = self.entrada_id_atualizar.get()
        dados = {coluna: entrada.get() for coluna, entrada in self.entries_atualizar}
        if tabela and rowid.isdigit() and all(dados.values()):
            self.db.alterar_linha(tabela, int(rowid), dados)
            messagebox.showinfo("Sucesso", "Registro atualizado com sucesso")
        else:
            messagebox.showwarning("Erro de Entrada", "Por favor, preencha todos os campos com dados válidos")

    def tab_excluir(self):
        ttk.Label(self.frame4, text="Selecione a Tabela:").grid(row=0, column=0, padx=10, pady=10)
        self.lista_tabelas_excluir = tk.StringVar()
        self.dropdown_tabelas_excluir = ttk.Combobox(self.frame4, textvariable=self.lista_tabelas_excluir)
        self.dropdown_tabelas_excluir.grid(row=0, column=1, padx=10, pady=10)
        self.dropdown_tabelas_excluir['values'] = self.db.listar_tabelas()

        ttk.Label(self.frame4, text="Número da Linha:").grid(row=1, column=0, padx=10, pady=10)
        self.entrada_numero_linha_excluir = ttk.Entry(self.frame4)
        self.entrada_numero_linha_excluir.grid(row=1, column=1, padx=10, pady=10)

        self.botao_excluir_linha = ttk.Button(self.frame4, text="Excluir Linha", command=self.excluir_linha)
        self.botao_excluir_linha.grid(row=2, column=0, columnspan=2, pady=10)

        self.botao_excluir_tabela = ttk.Button(self.frame4, text="Excluir Tabela", command=self.excluir_tabela)
        self.botao_excluir_tabela.grid(row=3, column=0, columnspan=2, pady=10)

    def excluir_linha(self):
        tabela = self.lista_tabelas_excluir.get()
        numero_linha = self.entrada_numero_linha_excluir.get()
        if tabela and numero_linha.isdigit():
            self.db.remover_linha_por_numero(tabela, int(numero_linha))
            messagebox.showinfo("Sucesso", "Linha excluída com sucesso")
        else:
            messagebox.showwarning("Erro de Entrada", "Por favor, insira um número de linha válido")

    def excluir_tabela(self):
        tabela = self.lista_tabelas_excluir.get()
        if tabela:
            self.db.excluir_tabela(tabela)
            self.dropdown_tabelas_excluir['values'] = self.db.listar_tabelas()
            messagebox.showinfo("Sucesso", "Tabela excluída com sucesso")
        else:
            messagebox.showwarning("Erro de Entrada", "Por favor, selecione uma tabela para excluir")

    def tab_nova_tabela(self):
        ttk.Label(self.frame5, text="Nome da Tabela:").grid(row=0, column=0, padx=10, pady=10)
        self.entrada_nome_tabela = ttk.Entry(self.frame5)
        self.entrada_nome_tabela.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self.frame5, text="Número de Colunas:").grid(row=1, column=0, padx=10, pady=10)
        self.numero_colunas = ttk.Spinbox(self.frame5, from_=1, to=10, width=5)
        self.numero_colunas.grid(row=1, column=1, padx=10, pady=10)
        self.numero_colunas.bind("<FocusOut>", self.gerar_entradas_colunas)

        self.entradas_colunas = []

    def gerar_entradas_colunas(self, event):
        for widget in self.frame5.grid_slaves():
            if int(widget.grid_info()["row"]) > 1:
                widget.grid_forget()

        num_colunas = int(self.numero_colunas.get())
        self.entradas_colunas = []
        for i in range(num_colunas):
            ttk.Label(self.frame5, text=f"Nome da Coluna {i + 1}:").grid(row=i + 2, column=0, padx=10, pady=10)
            entrada_nome_coluna = ttk.Entry(self.frame5)
            entrada_nome_coluna.grid(row=i + 2, column=1, padx=10, pady=10)
            self.entradas_colunas.append(entrada_nome_coluna)

        self.botao_criar_tabela = ttk.Button(self.frame5, text="Criar Tabela", command=self.criar_tabela)
        self.botao_criar_tabela.grid(row=num_colunas + 2, column=0, columnspan=2, pady=10)

    def criar_tabela(self):
        nome_tabela = self.entrada_nome_tabela.get()
        definicoes_colunas = [entrada.get() for entrada in self.entradas_colunas if entrada.get()]

        if not nome_tabela or not definicoes_colunas:
            messagebox.showwarning("Erro de Entrada", "Por favor, forneça um nome para a tabela e pelo menos uma coluna")
            return

        colunas_sql = ", ".join([f"{col} VARCHAR(100)" for col in definicoes_colunas])
        query = f"CREATE TABLE {nome_tabela} (id INT AUTO_INCREMENT PRIMARY KEY, {colunas_sql});"

        try:
            self.db.cur.execute(query)
            self.db.con.commit()
            messagebox.showinfo("Sucesso", f"Tabela '{nome_tabela}' criada com sucesso")
        except Error as e:
            messagebox.showerror("Erro ao Criar Tabela", f"Falha ao criar tabela: {e}")

if __name__ == '__main__':
    app = Aplicacao()
    app.mainloop()
