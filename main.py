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
            self.con.commit()
            logging.info("Registro inserido com sucesso")
        except Error as e:
            self.con.rollback()
            logging.error(f"Erro de Inserção: {e}")
            raise

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
            self.con.commit()
            logging.info("Registro atualizado com sucesso")
        except Error as e:
            self.con.rollback()
            logging.error(f"Erro de Atualização: {e}")
            raise

    def remover_linha(self, tabela, rowid):
        query = f'DELETE FROM {tabela} WHERE id = %s;'
        try:
            self.cur.execute(query, (rowid,))
            self.con.commit()
            logging.info("Registro removido com sucesso")
        except Error as e:
            self.con.rollback()
            logging.error(f"Erro de Remoção: {e}")
            raise

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
            self.con.commit()
            logging.info("Tabela excluída com sucesso")
        except Error as e:
            self.con.rollback()
            logging.error(f"Erro ao Excluir Tabela: {e}")
            raise

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
        self.geometry(None)
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.db = ConectarDB()

        self.criar_widgets()

    def criar_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, expand=True)

        self.frames = {}
        for tab in ["Criar", "Ler", "Atualizar", "Excluir", "Nova Tabela"]:
            frame = ttk.Frame(self.notebook, width=800, height=600)
            frame.pack(fill="both", expand=True)
            self.notebook.add(frame, text=tab)
            self.frames[tab] = frame

        self.tab_criar()
        self.tab_ler()
        self.tab_atualizar()
        self.tab_excluir()
        self.tab_nova_tabela()

    def tab_criar(self):
        frame = self.frames["Criar"]
        ttk.Label(frame, text="Selecione a Tabela:").grid(row=0, column=0, padx=10, pady=10)
        self.lista_tabelas_criar = tk.StringVar()
        self.dropdown_tabelas_criar = ttk.Combobox(frame, textvariable=self.lista_tabelas_criar)
        self.dropdown_tabelas_criar.grid(row=0, column=1, padx=10, pady=10)
        self.dropdown_tabelas_criar['values'] = self.db.listar_tabelas()
        self.dropdown_tabelas_criar.bind("<<ComboboxSelected>>", self.atualizar_formulario_criar)

        self.botao_atualizar_criar = ttk.Button(frame, text="Atualizar", command=self.atualizar_listas_tabelas)
        self.botao_atualizar_criar.grid(row=0, column=2, padx=10, pady=10)

        


        self.entries_criar = []
    
    def atualizar_formulario_criar(self, event):
        frame = self.frames["Criar"]
        for widget in frame.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:
                widget.grid_forget()
                
        tabela = self.lista_tabelas_criar.get()
        colunas = self.db.obter_colunas(tabela)

    
        self.entries_criar = []
        for idx, coluna in enumerate(colunas):
            if coluna == 'id':
                continue
            ttk.Label(frame, text=f"{coluna}:").grid(row=idx + 1, column=0, padx=10, pady=10)
            entrada = ttk.Entry(frame)
            entrada.grid(row=idx + 1, column=1, padx=10, pady=10)
            self.entries_criar.append((coluna, entrada))
        
        self.botao_criar = ttk.Button(frame, text="Adicionar Registro", command=self.adicionar_registro)
        self.botao_criar.grid(row=len(colunas) + 1, column=0, columnspan=2, pady=10)


    def tab_ler(self):
        frame = self.frames["Ler"]
        self.lista_tabelas = tk.StringVar()
        ttk.Label(frame, text="Selecione a Tabela:").grid(row=0, column=0, padx=10, pady=10)
        self.dropdown_tabelas = ttk.Combobox(frame, textvariable=self.lista_tabelas)
        self.dropdown_tabelas.grid(row=0, column=1, padx=10, pady=10)
        self.dropdown_tabelas['values'] = self.db.listar_tabelas()

        self.botao_atualizar_ler = ttk.Button(frame, text="Atualizar", command=self.atualizar_listas_tabelas)
        self.botao_atualizar_ler.grid(row=0, column=2, padx=10, pady=10)

        self.botao_ler = ttk.Button(frame, text="Buscar Registros", command=self.buscar_registros)
        self.botao_ler.grid(row=1, column=0, columnspan=2, pady=10)

        self.tree = ttk.Treeview(frame, show="headings")
        self.tree.grid(row=2, column=0, columnspan=2, pady=10)

        self.label_total_linhas = ttk.Label(frame, text="Total de Linhas: 0")
        self.label_total_linhas.grid(row=3, column=0, columnspan=2, pady=10)


    def adicionar_registro(self):
        tabela = self.lista_tabelas_criar.get()
        dados = {coluna: entrada.get() for coluna, entrada in self.entries_criar}
        if tabela and all(dados.values()):
            try:
                self.db.inserir_linha(tabela, dados)
                messagebox.showinfo("Sucesso", "Registro adicionado com sucesso")
                self.dropdown_tabelas_criar['values'] = self.db.listar_tabelas()
            except Error as e:
                messagebox.showerror("Erro de Inserção", f"Falha ao inserir registro: {e}")
        else:
            messagebox.showwarning("Erro de Entrada", "Por favor, preencha todos os campos com dados válidos")

    def tab_ler(self):
        frame = self.frames["Ler"]
        self.lista_tabelas = tk.StringVar()
        ttk.Label(frame, text="Selecione a Tabela:").grid(row=0, column=0, padx=10, pady=10)
        self.dropdown_tabelas = ttk.Combobox(frame, textvariable=self.lista_tabelas)
        self.dropdown_tabelas.grid(row=0, column=1, padx=10, pady=10)
        self.dropdown_tabelas['values'] = self.db.listar_tabelas()

        self.botao_atualizar_ler = ttk.Button(frame, text="Atualizar", command=self.atualizar_listas_tabelas)
        self.botao_atualizar_ler.grid(row=0, column=2, padx=10, pady=10)

        self.botao_ler = ttk.Button(frame, text="Buscar Registros", command=self.buscar_registros)
        self.botao_ler.grid(row=1, column=0, columnspan=2, pady=10)

        self.tree = ttk.Treeview(frame, show="headings")
        self.tree.grid(row=2, column=0, columnspan=2, pady=10)

        self.label_total_linhas = ttk.Label(frame, text="Total de Linhas: 0")
        self.label_total_linhas.grid(row=3, column=0, columnspan=2, pady=10)

    def buscar_registros(self):
        nome_tabela = self.lista_tabelas.get()
        if not nome_tabela:
            messagebox.showwarning("Erro de Entrada", "Por favor, selecione uma tabela")
            return

        try:
            colunas = self.db.obter_colunas(nome_tabela)
            registros = self.db.encontrar_linhas(nome_tabela)
            
            self.tree.delete(*self.tree.get_children())
            self.tree["columns"] = colunas
            for col in colunas:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100)
            
            for registro in registros:
                self.tree.insert("", tk.END, values=registro)
            
            self.label_total_linhas.config(text=f"Total de Linhas: {len(registros)}")
        except Error as e:
            messagebox.showerror("Erro de Leitura", f"Falha ao buscar registros: {e}")

    def tab_atualizar(self):
        frame = self.frames["Atualizar"]
        ttk.Label(frame, text="Selecione a Tabela:").grid(row=0, column=0, padx=10, pady=10)
        self.lista_tabelas_atualizar = tk.StringVar()
        self.dropdown_tabelas_atualizar = ttk.Combobox(frame, textvariable=self.lista_tabelas_atualizar)
        self.dropdown_tabelas_atualizar.grid(row=0, column=1, padx=10, pady=10)
        self.dropdown_tabelas_atualizar['values'] = self.db.listar_tabelas()
        self.dropdown_tabelas_atualizar.bind("<<ComboboxSelected>>", self.atualizar_formulario_atualizar)

        self.botao_atualizar_atualizar = ttk.Button(frame, text="Atualizar", command=self.atualizar_listas_tabelas)
        self.botao_atualizar_atualizar.grid(row=0, column=2, padx=10, pady=10)

        ttk.Label(frame, text="ID do Registro:").grid(row=1, column=0, padx=10, pady=10)
        self.entry_id_atualizar = ttk.Entry(frame)
        self.entry_id_atualizar.grid(row=1, column=1, padx=10, pady=10)

        self.botao_buscar_id = ttk.Button(frame, text="Buscar ID", command=self.buscar_registro_por_id)
        self.botao_buscar_id.grid(row=1, column=2, padx=10, pady=10)

        self.entries_atualizar = []

    def atualizar_formulario_atualizar(self, event):
        frame = self.frames["Atualizar"]
        for widget in frame.grid_slaves():
            if int(widget.grid_info()["row"]) > 1:
                widget.grid_forget()
                
        tabela = self.lista_tabelas_atualizar.get()
        colunas = self.db.obter_colunas(tabela)
        
        self.entries_atualizar = []
        for idx, coluna in enumerate(colunas):
            ttk.Label(frame, text=f"{coluna}:").grid(row=idx + 2, column=0, padx=10, pady=10)
            entrada = ttk.Entry(frame)
            entrada.grid(row=idx + 2, column=1, padx=10, pady=10)
            self.entries_atualizar.append((coluna, entrada))
        
        self.botao_atualizar = ttk.Button(frame, text="Atualizar Registro", command=self.atualizar_registro)
        self.botao_atualizar.grid(row=len(colunas) + 3, column=0, columnspan=2, pady=10)

    def buscar_registro_por_id(self):
        tabela = self.lista_tabelas_atualizar.get()
        rowid = self.entry_id_atualizar.get()
        if not tabela or not rowid:
            messagebox.showwarning("Erro de Entrada", "Por favor, preencha todos os campos com dados válidos")
            return

        try:
            registro = self.db.encontrar_linha_por_id(tabela, rowid)
            if registro:
                for (coluna, entrada), valor in zip(self.entries_atualizar, registro):
                    entrada.delete(0, tk.END)
                    entrada.insert(0, valor)
            else:
                messagebox.showinfo("Registro Não Encontrado", f"Registro com ID {rowid} não encontrado.")
        except Error as e:
            messagebox.showerror("Erro de Leitura", f"Falha ao buscar registro: {e}")

    def atualizar_registro(self):
        tabela = self.lista_tabelas_atualizar.get()
        rowid = self.entry_id_atualizar.get()
        dados = {coluna: entrada.get() for coluna, entrada in self.entries_atualizar}
        if tabela and rowid and all(dados.values()):
            try:
                self.db.alterar_linha(tabela, rowid, dados)
                messagebox.showinfo("Sucesso", "Registro atualizado com sucesso")
            except Error as e:
                messagebox.showerror("Erro de Atualização", f"Falha ao atualizar registro: {e}")
        else:
            messagebox.showwarning("Erro de Entrada", "Por favor, preencha todos os campos com dados válidos")

    def tab_excluir(self):
        frame = self.frames["Excluir"]
        ttk.Label(frame, text="Selecione a Tabela:").grid(row=0, column=0, padx=10, pady=10)
        self.lista_tabelas_excluir = tk.StringVar()
        self.dropdown_tabelas_excluir = ttk.Combobox(frame, textvariable=self.lista_tabelas_excluir)
        self.dropdown_tabelas_excluir.grid(row=0, column=1, padx=10, pady=10)
        self.dropdown_tabelas_excluir['values'] = self.db.listar_tabelas()

        self.botao_atualizar_excluir = ttk.Button(frame, text="Atualizar", command=self.atualizar_listas_tabelas)
        self.botao_atualizar_excluir.grid(row=0, column=2, padx=10, pady=10)

        ttk.Label(frame, text="ID do Registro:").grid(row=1, column=0, padx=10, pady=10)
        self.entry_id_excluir = ttk.Entry(frame)
        self.entry_id_excluir.grid(row=1, column=1, padx=10, pady=10)

        self.botao_excluir = ttk.Button(frame, text="Excluir Registro", command=self.excluir_registro)
        self.botao_excluir.grid(row=1, column=2, padx=10, pady=10)

        self.botao_excluir_tabela = ttk.Button(frame, text="Excluir Tabela", command=self.excluir_tabela)
        self.botao_excluir_tabela.grid(row=2, column=0, columnspan=3, pady=10)

    def excluir_registro(self):
        tabela = self.lista_tabelas_excluir.get()
        rowid = self.entry_id_excluir.get()
        if not tabela or not rowid:
            messagebox.showwarning("Erro de Entrada", "Por favor, preencha todos os campos com dados válidos")
            return

        try:
            self.db.remover_linha(tabela, rowid)
            messagebox.showinfo("Sucesso", "Registro excluído com sucesso")
            self.dropdown_tabelas_excluir['values'] = self.db.listar_tabelas()
        except Error as e:
            messagebox.showerror("Erro de Exclusão", f"Falha ao excluir registro: {e}")

    def excluir_tabela(self):
        tabela = self.lista_tabelas_excluir.get()
        if not tabela:
            messagebox.showwarning("Erro de Entrada", "Por favor, selecione uma tabela")
            return

        if messagebox.askyesno("Confirmação", f"Tem certeza que deseja excluir a tabela '{tabela}'?"):
            try:
                self.db.excluir_tabela(tabela)
                messagebox.showinfo("Sucesso", "Tabela excluída com sucesso")
                self.dropdown_tabelas_excluir['values'] = self.db.listar_tabelas()
            except Error as e:
                messagebox.showerror("Erro de Exclusão", f"Falha ao excluir tabela: {e}")

    def tab_nova_tabela(self):
        frame = self.frames["Nova Tabela"]
        ttk.Label(frame, text="Nome da Tabela:").grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.entry_nome_tabela = ttk.Entry(frame)
        self.entry_nome_tabela.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.entries_nova_tabela = []
        self.botao_add_coluna = ttk.Button(frame, text="Adicionar Coluna", command=self.add_coluna)
        self.botao_add_coluna.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.botao_remover_coluna = ttk.Button(frame, text="Remover Coluna", command=self.remover_coluna)
        self.botao_remover_coluna.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.botao_criar_tabela = ttk.Button(frame, text="Criar Tabela", command=self.criar_nova_tabela)
        self.botao_criar_tabela.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

    def add_coluna(self):
        frame = self.frames["Nova Tabela"]
        idx = len(self.entries_nova_tabela) + 3

        label_nome_coluna = ttk.Label(frame, text=f"Nome da Coluna {idx - 2}:")
        label_nome_coluna.grid(row=idx, column=0, padx=10, pady=10, sticky="w")
        entrada_nome_coluna = ttk.Entry(frame)
        entrada_nome_coluna.grid(row=idx, column=1, padx=10, pady=5, sticky="w")

        label_tipo_dado = ttk.Label(frame, text="Tipo de Dado:")
        label_tipo_dado.grid(row=idx, column=2, padx=10, pady=5, sticky="w")
        entrada_tipo_dado = ttk.Combobox(frame, values=["VARCHAR(100)", "INT", "FLOAT", "DATE", "TEXT"])
        entrada_tipo_dado.grid(row=idx, column=3, padx=10, pady=5, sticky="w")

        self.entries_nova_tabela.append((label_nome_coluna, entrada_nome_coluna, label_tipo_dado, entrada_tipo_dado))

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.columnconfigure(3, weight=1)

    def remover_coluna(self):
        if self.entries_nova_tabela:
            labels = self.entries_nova_tabela.pop()
            for label in labels:
                label.grid_forget()
            
    def criar_nova_tabela(self):
        nome_tabela = self.entry_nome_tabela.get().strip()
        colunas = [(entrada_nome.get().strip(), entrada_tipo.get().strip()) for entrada_nome, entrada_tipo in self.entries_nova_tabela if entrada_nome.get().strip() and entrada_tipo.get().strip()]

        if not nome_tabela or not colunas:
            messagebox.showwarning("Erro de Entrada", "Por favor, forneça um nome para a tabela e pelo menos uma coluna com seu tipo de dado")
            return

        colunas_sql = ", ".join([f"{nome} {tipo}" for nome, tipo in colunas])
        query = f"CREATE TABLE {nome_tabela} (id INT AUTO_INCREMENT PRIMARY KEY, {colunas_sql});"

        try:
            self.db.cur.execute(query)
            self.db.con.commit()
            messagebox.showinfo("Sucesso", "Tabela criada com sucesso")
            self.entry_nome_tabela.delete(0, tk.END)
            for entrada_nome, entrada_tipo in self.entries_nova_tabela:
                entrada_nome.delete(0, tk.END)
                entrada_tipo.set('')
            self.entries_nova_tabela = []
        except Error as e:
            messagebox.showerror("Erro de Criação", f"Falha ao criar tabela: {e}")


    def atualizar_listas_tabelas(self):
        tabelas = self.db.listar_tabelas()
        self.dropdown_tabelas_criar['values'] = tabelas
        self.dropdown_tabelas['values'] = tabelas
        self.dropdown_tabelas_atualizar['values'] = tabelas
        self.dropdown_tabelas_excluir['values'] = tabelas


if __name__ == "__main__":
    app = Aplicacao()
    app.mainloop()
