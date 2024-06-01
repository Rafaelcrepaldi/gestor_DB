from email.mime import application
import os
import re
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
import mysql.connector
from mysql.connector import connect, Error
import logging
import ttkthemes

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
        if not tabela:
            raise ValueError("Table name must be provided.")
        
        query = f"SHOW COLUMNS FROM `{tabela}`"
        print(f"Executing query: {query}")  # Debugging statement
        
        try:
            self.cur.execute(query)
            colunas = self.cur.fetchall()
            return colunas
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return []
        
    def obter_nomes_colunas(self, tabela):
        if not tabela:
            raise ValueError("Table name must be provided.")
        
        query = f"SHOW COLUMNS FROM `{tabela}`"
        print(f"Executing query: {query}")  # Debugging statement
        
        try:
            self.cur.execute(query)
            colunas = self.cur.fetchall()
            nomes_colunas = [coluna[0] for coluna in colunas]  # Extrai o nome de cada coluna
            return nomes_colunas
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return []

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
        
    def exportar_para_sql(self, tabela, caminho_arquivo):
        try:
            query = f'SELECT * FROM {tabela};'
            self.cur.execute(query)
            registros = self.cur.fetchall()
            if registros:
                colunas = self.obter_colunas(tabela)
                with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo_sql:
                    arquivo_sql.write(f"CREATE TABLE {tabela} (\n")
                    for i, coluna in enumerate(colunas):
                        arquivo_sql.write(f"    {coluna[0]} {coluna[1]}")
                        if i < len(colunas) - 1:
                            arquivo_sql.write(",\n")
                        else:
                            arquivo_sql.write("\n")
                    arquivo_sql.write(");\n")
                    for registro in registros:
                        valores = ', '.join([f"'{str(valor)}'" for valor in registro])
                        arquivo_sql.write(f"INSERT INTO {tabela} ({', '.join(coluna[0] for coluna in colunas)}) VALUES ({valores});\n")
                logging.info(f"Tabela {tabela} exportada com sucesso para {caminho_arquivo}")
            else:
                logging.warning(f"A consulta SQL não retornou resultados para a tabela {tabela}")
        except Error as e:
            logging.error(f"Erro ao exportar tabela {tabela}: {e}")
            raise

    def importar_de_sql(self, caminho_arquivo, tabela):
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo_sql:
                sql_script = arquivo_sql.read()
                self.cur.execute(f"DROP TABLE IF EXISTS {tabela}")
                self.cur.execute(sql_script)
                self.con.commit()
            logging.info(f"Tabela {tabela} importada com sucesso de {caminho_arquivo}")
        except Error as e:
            logging.error(f"Erro ao importar tabela {tabela}: {e}")
            raise

    def listar_tabelas_apos_criacao(self):
        query = "SHOW TABLES;"
        try:
            self.cur.execute(query)
            tabelas = self.cur.fetchall()
            return [tabela[0] for tabela in tabelas]
        except Error as e:
            logging.error(f"Erro ao listar tabelas após criação: {e}")
            raise

class Aplicacao(tk.Frame):  # Inherit from tk.Frame
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(fill="both", expand=True)

        self.master.title("Interface CRUD")
        self.master.geometry(None)

        self.style = ttkthemes.ThemedStyle(self)
        self.style.set_theme("equilux")

        self.db = ConectarDB()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.frames = {}
        for tab in ["Importar/Exportar", "Criar", "Ler", "Atualizar", "Excluir", "Nova Tabela", "Editor SQL"]:
            frame = ttk.Frame(self.notebook)
            frame.grid(row=0, column=0, sticky="nsew") 
            self.notebook.add(frame, text=tab)
            self.frames[tab] = frame

        self.tab_importar_exportar()
        self.tab_criar()
        self.tab_ler()
        self.tab_atualizar()
        self.tab_excluir()
        self.tab_nova_tabela()
        self.tab_editor_sql()

    def tab_nova_tabela(self):
        frame = self.frames["Nova Tabela"]

        ttk.Label(frame, text="Nome da Tabela:").grid(row=0, column=0, padx=10, pady=10)
        self.nome_tabela = ttk.Entry(frame)
        self.nome_tabela.grid(row=0, column=1, padx=10, pady=10)

        self.frame_colunas = ttk.Frame(frame)
        self.frame_colunas.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self.lista_colunas = []
        self.adicionar_linha_coluna()

        ttk.Button(frame, text="Adicionar Coluna", command=self.adicionar_linha_coluna).grid(row=2, column=0, padx=10, pady=10)
        ttk.Button(frame, text="Remover Coluna", command=self.remover_linha_coluna).grid(row=2, column=1, padx=10, pady=10)
        ttk.Button(frame, text="Criar Tabela", command=self.criar_tabela).grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def adicionar_linha_coluna(self):
        linha = len(self.lista_colunas)
        nome_coluna = ttk.Entry(self.frame_colunas)
        nome_coluna.grid(row=linha, column=0, padx=10, pady=10)
        tipo_coluna = ttk.Combobox(self.frame_colunas, values=["INT", "VARCHAR(100)", "TEXT", "DATE"])
        tipo_coluna.grid(row=linha, column=1, padx=10, pady=10)
        self.lista_colunas.append((nome_coluna, tipo_coluna))

    def remover_linha_coluna(self):
        if self.lista_colunas:
            nome_coluna, tipo_coluna = self.lista_colunas.pop()
            nome_coluna.destroy()
            tipo_coluna.destroy()

    def criar_tabela(self):
        nome_tabela = self.nome_tabela.get()
        if not nome_tabela:
            messagebox.showerror("Erro", "Nome da tabela não pode estar vazio")
            return
        colunas = []
        for nome_coluna, tipo_coluna in self.lista_colunas:
            if not nome_coluna.get() or not tipo_coluna.get():
                messagebox.showerror("Erro", "Nome e tipo da coluna não podem estar vazios")
                return
            colunas.append(f"{nome_coluna.get()} {tipo_coluna.get()}")
        query = f"CREATE TABLE {nome_tabela} ({', '.join(colunas)});"
        try:
            self.db.cur.execute(query)
            self.db.con.commit()
            messagebox.showinfo("Sucesso", f"Tabela '{nome_tabela}' criada com sucesso")
            self.atualizar_lista_tabelas()
        except Error as e:
            messagebox.showerror("Erro", f"Falha ao criar tabela: {e}")

    def atualizar_lista_tabelas(self):
        tabelas = self.db.listar_tabelas()
        self.combo_tabelas['values'] = tabelas

    def tab_importar_exportar(self):
        frame = self.frames["Importar/Exportar"]

        ttk.Label(frame, text="Tabela:").grid(row=0, column=0, padx=10, pady=10)
        self.combo_tabelas = ttk.Combobox(frame)
        self.combo_tabelas.grid(row=0, column=1, padx=10, pady=10)
        self.atualizar_lista_tabelas()

        ttk.Button(frame, text="Exportar Tabela", command=self.exportar_tabela).grid(row=1, column=0, padx=10, pady=10)
        ttk.Button(frame, text="Importar Tabela", command=self.importar_tabela).grid(row=1, column=1, padx=10, pady=10)

    def exportar_tabela(self):
        tabela = self.combo_tabelas.get()
        if not tabela:
            messagebox.showerror("Erro", "Nenhuma tabela selecionada para exportação")
            return

        caminho_arquivo = filedialog.asksaveasfilename(defaultextension=".sql", filetypes=[("SQL files", "*.sql"), ("All files", "*.*")])
        if not caminho_arquivo:
            return  # usuário cancelou a seleção do arquivo

        try:
            self.db.exportar_para_sql(tabela, caminho_arquivo)
            messagebox.showinfo("Sucesso", f"Tabela '{tabela}' exportada com sucesso para '{caminho_arquivo}'")
        except Error as e:
            messagebox.showerror("Erro", f"Falha ao exportar tabela: {e}")

    def importar_tabela(self):
        caminho_arquivo = filedialog.askopenfilename(filetypes=[("SQL files", "*.sql"), ("All files", "*.*")])
        if not caminho_arquivo:
            return  # usuário cancelou a seleção do arquivo

        nome_tabela = filedialog.askstring("Nome da Tabela", "Digite o nome da tabela para importar:")
        if not nome_tabela:
            messagebox.showerror("Erro", "Nome da tabela não pode estar vazio")
            return

        try:
            self.db.importar_de_sql(caminho_arquivo, nome_tabela)
            messagebox.showinfo("Sucesso", f"Tabela '{nome_tabela}' importada com sucesso de '{caminho_arquivo}'")
            self.atualizar_lista_tabelas()
        except Error as e:
            messagebox.showerror("Erro", f"Falha ao importar tabela: {e}")

    def tab_criar(self):
        frame = self.frames["Criar"]
        ttk.Label(frame, text="Tabela:").grid(row=0, column=0, padx=10, pady=10)
        self.combo_tabelas_criar = ttk.Combobox(frame)
        self.combo_tabelas_criar.grid(row=0, column=1, padx=10, pady=10)
        self.combo_tabelas_criar['values'] = self.db.listar_tabelas()

        self.botao_carregar_colunas = ttk.Button(frame, text="Carregar Colunas", command=self.carregar_colunas)
        self.botao_carregar_colunas.grid(row=0, column=2, padx=10, pady=10)

        self.frame_colunas_criar = ttk.Frame(frame)
        self.frame_colunas_criar.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        self.colunas_criar = []

        self.botao_inserir = ttk.Button(frame, text="Inserir", command=self.inserir_linha)
        self.botao_inserir.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

    def carregar_colunas(self):
        tabela = self.combo_tabelas_criar.get()
        if not tabela:
            messagebox.showerror("Erro", "Nenhuma tabela selecionada")
            return

        for widget in self.frame_colunas_criar.winfo_children():
            widget.destroy()

        self.colunas_criar = []

        try:
            colunas = self.db.obter_colunas(tabela)
            for i, coluna in enumerate(colunas):
                ttk.Label(self.frame_colunas_criar, text=coluna[0]).grid(row=i, column=0, padx=10, pady=10)
                entrada = ttk.Entry(self.frame_colunas_criar)
                entrada.grid(row=i, column=1, padx=10, pady=10)
                self.colunas_criar.append((coluna[0], entrada))
        except Error as e:
            messagebox.showerror("Erro", f"Falha ao obter colunas: {e}")

    def inserir_linha(self):
        tabela = self.combo_tabelas_criar.get()
        if not tabela:
            messagebox.showerror("Erro", "Nenhuma tabela selecionada")
            return

        dados = {}
        for coluna, entrada in self.colunas_criar:
            dados[coluna] = entrada.get()

        try:
            self.db.inserir_linha(tabela, dados)
            messagebox.showinfo("Sucesso", "Registro inserido com sucesso")
        except Error as e:
            messagebox.showerror("Erro", f"Falha ao inserir linha: {e}")

    def tab_ler(self):
        frame = self.frames["Ler"]

        ttk.Label(frame, text="Tabela:").grid(row=0, column=0, padx=10, pady=10)
        self.combo_tabelas_ler = ttk.Combobox(frame)
        self.combo_tabelas_ler.grid(row=0, column=1, padx=10, pady=10)
        self.combo_tabelas_ler['values'] = self.db.listar_tabelas()

        self.botao_carregar_dados = ttk.Button(frame, text="Carregar Dados", command=self.carregar_dados)
        self.botao_carregar_dados.grid(row=0, column=2, padx=10, pady=10)

        self.frame_dados = ttk.Frame(frame)
        self.frame_dados.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

    def carregar_dados(self):
        tabela = self.combo_tabelas_ler.get()
        if not tabela:
            messagebox.showerror("Erro", "Nenhuma tabela selecionada")
            return

        for widget in self.frame_dados.winfo_children():
            widget.destroy()

        try:
            colunas = self.db.obter_nomes_colunas(tabela)
            dados = self.db.encontrar_linhas(tabela)

            for i, coluna in enumerate(colunas):
                ttk.Label(self.frame_dados, text=coluna).grid(row=0, column=i, padx=10, pady=10)

            for i, linha in enumerate(dados, start=1):
                for j, valor in enumerate(linha):
                    ttk.Label(self.frame_dados, text=valor).grid(row=i, column=j, padx=10, pady=10)
        except Error as e:
            messagebox.showerror("Erro", f"Falha ao carregar dados: {e}")

    def tab_excluir(self):
        frame = self.frames["Excluir"]

        ttk.Label(frame, text="Tabela:").grid(row=0, column=0, padx=10, pady=10)
        self.combo_tabelas_excluir = ttk.Combobox(frame)
        self.combo_tabelas_excluir.grid(row=0, column=1, padx=10, pady=10)
        self.combo_tabelas_excluir['values'] = self.db.listar_tabelas()

        self.botao_carregar_colunas_excluir = ttk.Button(frame, text="Carregar Colunas", command=self.carregar_colunas_excluir)
        self.botao_carregar_colunas_excluir.grid(row=0, column=2, padx=10, pady=10)

        self.frame_colunas_excluir = ttk.Frame(frame)
        self.frame_colunas_excluir.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        self.colunas_excluir = []

        self.botao_excluir = ttk.Button(frame, text="Excluir", command=self.excluir_linha)
        self.botao_excluir.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

    def carregar_colunas_excluir(self):
        tabela = self.combo_tabelas_excluir.get()
        if not tabela:
            messagebox.showerror("Erro", "Nenhuma tabela selecionada")
            return

        for widget in self.frame_colunas_excluir.winfo_children():
            widget.destroy()

        self.colunas_excluir = []

        try:
            colunas = self.db.obter_colunas(tabela)
            for i, coluna in enumerate(colunas):
                ttk.Label(self.frame_colunas_excluir, text=coluna[0]).grid(row=i, column=0, padx=10, pady=10)
                entrada = ttk.Entry(self.frame_colunas_excluir)
                entrada.grid(row=i, column=1, padx=10, pady=10)
                self.colunas_excluir.append((coluna[0], entrada))
        except Error as e:
            messagebox.showerror("Erro", f"Falha ao obter colunas: {e}")

    def excluir_linha(self):
        tabela = self.combo_tabelas_excluir.get()
        if not tabela:
            messagebox.showerror("Erro", "Nenhuma tabela selecionada")
            return

        condicoes = {}
        for coluna, entrada in self.colunas_excluir:
            if entrada.get():
                condicoes[coluna] = entrada.get()

        try:
            self.db.excluir_linha(tabela, condicoes)
            messagebox.showinfo("Sucesso", "Registro excluído com sucesso")
        except Error as e:
            messagebox.showerror("Erro", f"Falha ao excluir linha: {e}")

    def tab_atualizar(self):
        frame = self.frames["Atualizar"]
        ttk.Label(frame, text="Selecione a Tabela:").grid(row=0, column=0, padx=10, pady=10)
        self.lista_tabelas_atualizar = tk.StringVar()
        self.dropdown_tabelas_atualizar = ttk.Combobox(frame, textvariable=self.lista_tabelas_atualizar)
        self.dropdown_tabelas_atualizar.grid(row=0, column=1, padx=10, pady=10)
        self.dropdown_tabelas_atualizar['values'] = self.db.listar_tabelas()
        self.dropdown_tabelas_atualizar.bind("<<ComboboxSelected>>", self.atualizar_formulario_atualizar)

        self.botao_atualizar_atualizar = ttk.Button(frame, text="Atualizar", command=self.atualizar_lista_tabelas)
        self.botao_atualizar_atualizar.grid(row=0, column=2, padx=10, pady=10)

        self.entries_atualizar = []
    def atualizar_formulario_atualizar(self, event):
        frame = self.frames["Atualizar"]
        for widget in frame.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:
                widget.grid_forget()
                
        tabela = self.lista_tabelas_atualizar.get()
        colunas = self.db.obter_nomes_colunas(tabela)

        self.entries_atualizar = []
        for idx, coluna in enumerate(colunas):
            ttk.Label(frame, text=f"{coluna}:").grid(row=idx + 1, column=0, padx=10, pady=10)
            entrada = ttk.Entry(frame)
            entrada.grid(row=idx + 1, column=1, padx=10, pady=10)
            self.entries_atualizar.append((coluna, entrada))
        
        self.botao_buscar_id = ttk.Button(frame, text="Buscar ID", command=self.buscar_id)
        self.botao_buscar_id.grid(row=len(colunas) + 1, column=0, pady=10)

        self.botao_atualizar_registro = ttk.Button(frame, text="Atualizar Registro", command=self.atualizar_registro)
        self.botao_atualizar_registro.grid(row=len(colunas) + 1, column=1, pady=10)

    def buscar_id(self):
        tabela = self.lista_tabelas_atualizar.get()
        id_buscar = self.entries_atualizar[0][1].get()
        if tabela and id_buscar:
            try:
                registro = self.db.encontrar_linha_por_id(tabela, id_buscar)
                if registro:
                    for entrada, valor in zip(self.entries_atualizar, registro):
                        entrada[1].delete(0, tk.END)
                        entrada[1].insert(0, valor)
                else:
                    messagebox.showwarning("Registro Não Encontrado", "Nenhum registro encontrado com o ID fornecido")
            except Error as e:
                messagebox.showerror("Erro de Busca", f"Falha ao buscar registro: {e}")
        else:
            messagebox.showwarning("Erro de Entrada", "Por favor, selecione uma tabela e forneça um ID")

    def atualizar_registro(self):
        tabela = self.lista_tabelas_atualizar.get()
        dados = {coluna: entrada.get() for coluna, entrada in self.entries_atualizar if coluna != 'id'}
        rowid = self.entries_atualizar[0][1].get()
        if tabela and rowid and all(dados.values()):
            try:
                self.db.alterar_linha(tabela, rowid, dados)
                messagebox.showinfo("Sucesso", "Registro atualizado com sucesso")
            except Error as e:
                messagebox.showerror("Erro de Atualização", f"Falha ao atualizar registro: {e}")
        else:
            messagebox.showwarning("Erro de Entrada", "Por favor, preencha todos os campos com dados válidos")
    
    def tab_editor_sql(self):
        frame = self.frames["Editor SQL"]

        self.texto_sql = tk.Text(frame, wrap="word", width=100, height=20)
        self.texto_sql.pack(padx=10, pady=10)

        self.botao_executar_sql = ttk.Button(frame, text="Executar SQL", command=self.executar_sql)
        self.botao_executar_sql.pack(pady=10)

        self.resultados_sql = tk.Text(frame, wrap="word", width=100, height=10, state="disabled")
        self.resultados_sql.pack(padx=10, pady=10)

        self.botao_exportar = ttk.Button(frame, text="Exportar Resultados", command=self.exportar_resultados)
        self.botao_exportar.pack(pady=10)

    def executar_sql(self):
        query = self.texto_sql.get("1.0", "end-1c").strip()
        if not query:
            messagebox.showwarning("Atenção", "Por favor, insira um comando SQL.")
            return

        try:
            self.db.cur.execute(query)
            if query.upper().startswith("SELECT"):
                resultados = self.db.cur.fetchall()
                colunas = [desc[0] for desc in self.db.cur.description]

                self.resultados_sql.config(state="normal")
                self.resultados_sql.delete("1.0", "end")

                # Escrever cabeçalhos das colunas
                self.resultados_sql.insert("end", "\t".join(colunas) + "\n")
                # Escrever registros
                for row in resultados:
                    self.resultados_sql.insert("end", "\t".join(map(str, row)) + "\n")

                self.resultados_sql.config(state="disabled")
                self.resultados_obtidos = {"colunas": colunas, "dados": resultados}
            else:
                self.db.con.commit()
                self.resultados_sql.config(state="normal")
                self.resultados_sql.delete("1.0", "end")
                self.resultados_sql.insert("end", "Comando SQL executado com sucesso.")
                self.resultados_sql.config(state="disabled")
                self.resultados_obtidos = None

                messagebox.showinfo("Sucesso", "Comando SQL executado com sucesso")
        except Error as e:
            self.resultados_sql.config(state="normal")
            self.resultados_sql.delete("1.0", "end")
            self.resultados_sql.insert("end", f"Falha ao executar comando SQL: {e}")
            self.resultados_sql.config(state="disabled")
            messagebox.showerror("Erro de Execução", f"Falha ao executar comando SQL: {e}")
    

    def exportar_resultados(self):
        if not hasattr(self, 'resultados_obtidos') or self.resultados_obtidos is None:
            messagebox.showwarning("Atenção", "Não há resultados para exportar.")
            return

        arquivo = filedialog.asksaveasfilename(defaultextension=".sql", filetypes=[("Arquivos SQL", "*.sql")])
        if not arquivo:
            return

        tabela = input("Nome da tabela para exportar os resultados: ")  # Solicita o nome da tabela
        if not tabela:
            messagebox.showwarning("Atenção", "Por favor, insira o nome da tabela.")
            return

        colunas = self.resultados_obtidos.get("colunas", [])
        dados = self.resultados_obtidos.get("dados", [])

        try:
            with open(arquivo, mode='w', newline='') as file:
                file.write(f"CREATE TABLE {tabela} (\n")
                for coluna in colunas:
                    file.write(f"    {coluna} TEXT,\n")
                file.write(");\n")
                for registro in dados:
                    valores = ', '.join([f"'{str(valor)}'" for valor in registro])
                    file.write(f"INSERT INTO {tabela} VALUES ({valores});\n")
            messagebox.showinfo("Sucesso", "Resultados exportados com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar resultados: {e}")



if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacao(master=root)
    app.mainloop()
