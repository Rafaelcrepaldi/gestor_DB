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
                        arquivo_sql.write(f"    {coluna} TEXT")
                        if i < len(colunas) - 1:
                            arquivo_sql.write(",\n")
                        else:
                            arquivo_sql.write("\n")
                    arquivo_sql.write(");\n")
                    for registro in registros:
                        valores = ', '.join([f"'{str(valor)}'" for valor in registro])
                        arquivo_sql.write(f"INSERT INTO {tabela} ({', '.join(colunas)}) VALUES ({valores});\n")
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
        self.pack()

        self.master.title("Interface CRUD")
        self.master.geometry(None)

        self.style = ttkthemes.ThemedStyle(self)
        self.style.set_theme("adapta")

        self.db = ConectarDB()

        self.criar_widgets()

    def criar_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, expand=True)

        self.frames = {}
        for tab in ["Importar/Exportar","Criar", "Ler", "Atualizar", "Excluir", "Nova Tabela", "Editor SQL"]:
            frame = ttk.Frame(self.notebook, width=800, height=600)
            frame.pack(fill="both", expand=True)
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
        self.frame_colunas.grid(row=1, column=0, columnspan=2, pady=10)

        self.colunas = []
        self.adicionar_coluna()

        self.botao_adicionar_coluna = ttk.Button(frame, text="Adicionar Coluna", command=self.adicionar_coluna)
        self.botao_adicionar_coluna.grid(row=2, column=0, columnspan=2, pady=10)

        self.botao_criar_tabela = ttk.Button(frame, text="Criar Tabela", command=self.criar_tabela)
        self.botao_criar_tabela.grid(row=3, column=0, columnspan=2, pady=10)

    def adicionar_coluna(self):
        row = len(self.colunas)
        frame_coluna = ttk.Frame(self.frame_colunas)
        frame_coluna.grid(row=row, column=0, padx=10, pady=5, sticky="w")

        ttk.Label(frame_coluna, text=f"Coluna {row+1}").grid(row=0, column=0, padx=10, pady=5)
        entrada_coluna = ttk.Entry(frame_coluna)
        entrada_coluna.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(frame_coluna, text="Tipo").grid(row=0, column=2, padx=10, pady=5)
        entrada_tipo = ttk.Combobox(frame_coluna, values=["INTEGER", "TEXT", "REAL", "BLOB", "NUMERIC"])
        entrada_tipo.grid(row=0, column=3, padx=10, pady=5)

        botao_excluir = ttk.Button(frame_coluna, text="Excluir", command=lambda: self.excluir_coluna(frame_coluna))
        botao_excluir.grid(row=0, column=4, padx=10, pady=5)

        self.colunas.append((frame_coluna, entrada_coluna, entrada_tipo))

    def excluir_coluna(self, frame_coluna):
        for idx, (frame, _, _) in enumerate(self.colunas):
            if frame == frame_coluna:
                self.colunas.pop(idx)
                frame_coluna.destroy()
                break

    def criar_tabela(self):
        nome_tabela = self.nome_tabela.get().strip()
        if not nome_tabela:
            messagebox.showwarning("Erro de Entrada", "Por favor, insira um nome para a tabela.")
            return

        colunas = []
        for frame, entrada_coluna, entrada_tipo in self.colunas:
            coluna = entrada_coluna.get().strip()
            tipo = entrada_tipo.get().strip()
            if coluna and tipo:
                colunas.append(f"{coluna} {tipo}")
            else:
                messagebox.showwarning("Erro de Entrada", "Por favor, preencha todos os campos de coluna e tipo.")
                return

        if colunas:
            query = f"CREATE TABLE {nome_tabela} ({', '.join(colunas)});"
            try:
                self.db.cur.execute(query)
                self.db.con.commit()
                messagebox.showinfo("Sucesso", f"Tabela {nome_tabela} criada com sucesso")
                self.atualizar_listas_tabelas()
            except Error as e:
                messagebox.showerror("Erro de Criação", f"Falha ao criar tabela: {e}")
        else:
            messagebox.showwarning("Erro de Entrada", "Por favor, adicione pelo menos uma coluna.")



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
        colunas = self.db.obter_nomes_colunas(tabela)

    
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

        ttk.Label(frame, text="Tabela:").grid(row=0, column=0, padx=10, pady=10)
        
        self.checkboxes = []
        self.var_checkboxes = []
        
        # Botão para atualizar as tabelas disponíveis
        self.botao_atualizar_tabelas = ttk.Button(frame, text="Atualizar Tabelas", command=self.atualizar_tabelas_disponiveis)
        self.botao_atualizar_tabelas.grid(row=0, column=1, padx=10, pady=10)
        
        # Placeholder for checkboxes
        self.checkboxes_frame = ttk.Frame(frame)
        self.checkboxes_frame.grid(row=1, column=0, columnspan=2, sticky="w")

        self.botao_mostrar_tabelas = ttk.Button(frame, text="Mostrar Tabelas", command=self.mostrar_tabelas_selecionadas)
        self.botao_mostrar_tabelas.grid(row=2, column=0, columnspan=2, pady=10)

        self.tabela_resultado = ttk.Treeview(frame)
        self.tabela_resultado.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Atualizar as tabelas disponíveis ao carregar o frame
        self.atualizar_tabelas_disponiveis()

    def atualizar_tabelas_disponiveis(self):
        # Limpar checkboxes existentes
        for widget in self.checkboxes_frame.winfo_children():
            widget.destroy()
        
        self.checkboxes = []
        self.var_checkboxes = []
        tabelas = self.db.listar_tabelas()
        
        for tabela in tabelas:
            var = tk.BooleanVar()
            checkbox = ttk.Checkbutton(self.checkboxes_frame, text=tabela, variable=var)
            checkbox.grid(sticky="w")
            self.checkboxes.append(checkbox)
            self.var_checkboxes.append(var)

    def mostrar_tabelas_selecionadas(self):
        tabelas_selecionadas = [tabela.cget("text") for tabela, var in zip(self.checkboxes, self.var_checkboxes) if var.get()]

        # Limpar a Treeview antes de inserir novas linhas
        for item in self.tabela_resultado.get_children():
            self.tabela_resultado.delete(item)
            
        for tabela in tabelas_selecionadas:
            linhas = self.db.encontrar_linhas(tabela)
            colunas = self.db.obter_nomes_colunas(tabela)
            
            # Configurar as colunas da Treeview
            self.tabela_resultado["columns"] = colunas
            self.tabela_resultado["show"] = "headings"  # Ocultar a primeira coluna que é a coluna padrão vazia
            
            for col in colunas:
                self.tabela_resultado.heading(col, text=col)
                self.tabela_resultado.column(col, width=100)  # Ajustar a largura da coluna conforme necessário
            
            for linha in linhas:
                self.tabela_resultado.insert("", "end", values=linha)


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

    def tab_excluir(self):
        frame = self.frames["Excluir"]
        ttk.Label(frame, text="Selecione a Tabela:").grid(row=0, column=0, padx=10, pady=10)
        self.lista_tabelas_excluir = tk.StringVar()
        self.dropdown_tabelas_excluir = ttk.Combobox(frame, textvariable=self.lista_tabelas_excluir)
        self.dropdown_tabelas_excluir.grid(row=0, column=1, padx=10, pady=10)
        self.dropdown_tabelas_excluir['values'] = self.db.listar_tabelas()

        self.botao_atualizar_excluir = ttk.Button(frame, text="Atualizar", command=self.atualizar_listas_tabelas)
        self.botao_atualizar_excluir.grid(row=0, column=2, padx=10, pady=10)

        self.id_excluir = ttk.Entry(frame)
        self.id_excluir.grid(row=1, column=1, padx=10, pady=10)

        self.botao_excluir = ttk.Button(frame, text="Excluir Registro", command=self.excluir_registro)
        self.botao_excluir.grid(row=2, column=0, columnspan=3, pady=10)

        self.botao_excluir_tabela = ttk.Button(frame, text="Excluir Tabela", command=self.excluir_tabela)
        self.botao_excluir_tabela.grid(row=3, column=0, columnspan=3, pady=10)

    def excluir_registro(self):
        tabela = self.lista_tabelas_excluir.get()
        rowid = self.id_excluir.get()
        if tabela and rowid:
            try:
                self.db.remover_linha(tabela, rowid)
                messagebox.showinfo("Sucesso", "Registro excluído com sucesso")
                self.dropdown_tabelas_excluir['values'] = self.db.listar_tabelas()
            except Error as e:
                messagebox.showerror("Erro de Exclusão", f"Falha ao excluir registro: {e}")
        else:
            messagebox.showwarning("Erro de Entrada", "Por favor, selecione uma tabela e forneça um ID")

    def excluir_tabela(self):
        tabela = self.lista_tabelas_excluir.get()
        if tabela:
            if messagebox.askyesno("Confirmação", f"Tem certeza que deseja excluir a tabela {tabela}?"):
                try:
                    self.db.excluir_tabela(tabela)
                    messagebox.showinfo("Sucesso", "Tabela excluída com sucesso")
                    self.dropdown_tabelas_excluir['values'] = self.db.listar_tabelas()
                except Error as e:
                    messagebox.showerror("Erro de Exclusão", f"Falha ao excluir tabela: {e}")
        else:
            messagebox.showwarning("Erro de Entrada", "Por favor, selecione uma tabela")

    
    def tab_importar_exportar(self):
        frame = self.frames["Importar/Exportar"]

        ttk.Label(frame, text="Selecione a Tabela:").grid(row=0, column=0, padx=10, pady=10)
        self.lista_tabelas_ = tk.StringVar()
        self.dropdown_tabelas_importar_exportar = ttk.Combobox(frame, textvariable=self.atualizar_listas_tabelas)
        self.dropdown_tabelas_importar_exportar.grid(row=0, column=1, padx=10, pady=10)
        self.dropdown_tabelas_importar_exportar['values'] = self.db.listar_tabelas()

        self.botao_atualizar_importar_exportar = ttk.Button(frame, text="Atualizar", command=self.atualizar_listas_tabelas)
        self.botao_atualizar_importar_exportar.grid(row=0, column=2, padx=10, pady=10)

        self.botao_exportar = ttk.Button(frame, text="Exportar", command=self.exportar_tabela)
        self.botao_exportar.grid(row=1, column=0, padx=10, pady=10)

        self.botao_importar = ttk.Button(frame, text="Importar", command=self.importar_tabela)
        self.botao_importar.grid(row=1, column=1, padx=10, pady=10)

        

    def exportar_tabela(self):
        tabela = self.combo_tabelas.get().strip()
        if not tabela:
            messagebox.showerror("Erro", "Selecione uma tabela para exportar")
            return

        caminho_arquivo = filedialog.asksaveasfilename(defaultextension=".sql", filetypes=[("SQL Files", "*.sql")])
        if not caminho_arquivo:
            return

        try:
            self.db.exportar_para_sql(tabela, caminho_arquivo)
            messagebox.showinfo("Sucesso", f"Tabela {tabela} exportada com sucesso para {caminho_arquivo}")
        except Error as e:
            messagebox.showerror("Erro", f"Erro ao exportar tabela: {e}")

    import re

    def importar_tabela(self):
        caminho_arquivo = filedialog.askopenfilename(filetypes=[("SQL Files", "*.sql")])
        if not caminho_arquivo:
            return

        nome_tabela = os.path.splitext(os.path.basename(caminho_arquivo))[0]

        try:
            with open(caminho_arquivo, 'r') as arquivo:
                sql_script = arquivo.read()

            # Dividir o script SQL em comandos individuais
            sql_commands = re.split(';\s*\n', sql_script)

            # Executar cada comando individualmente
            for command in sql_commands:
                if command.strip():
                    if command.lower().startswith('create table'):
                        # Se o comando for uma declaração CREATE TABLE,
                        # extraímos o nome da tabela e as colunas
                        table_name_match = re.search(r'CREATE TABLE\s+(\w+)\s*\((.*)\)', command, re.IGNORECASE)
                        if table_name_match:
                            table_name = table_name_match.group(1)
                            column_defs = table_name_match.group(2).split(',')
                            column_names = [col.strip().split()[0] for col in column_defs]
                            column_names_str = ', '.join(column_names)
                            command = f'CREATE TABLE {table_name} ({table_name}ID INTEGER PRIMARY KEY AUTOINCREMENT, {", ".join(column_defs)})'
                    
                    self.db.cur.execute(command.strip())

            self.db.con.commit()
            messagebox.showinfo("Sucesso", f"Tabela {nome_tabela} importada com sucesso de {caminho_arquivo}")

        except Error as e:
            self.db.con.rollback()
            messagebox.showerror("Erro", f"Erro ao importar tabela: {e}")

        # Atualizar a lista de tabelas
        self.combo_tabelas['values'] = self.db.listar_tabelas()
        self.combo_tabelas_criar['values'] = self.db.listar_tabelas()
        self.combo_tabelas_ler['values'] = self.db.listar_tabelas()
        self.combo_tabelas_atualizar['values'] = self.db.listar_tabelas()
        self.combo_tabelas_excluir['values'] = self.db.listar_tabelas()

    def atualizar_listas_tabelas(self):
        tabelas = self.db.listar_tabelas()
        self.dropdown_tabelas_importar_exportar['values'] = tabelas
        self.dropdown_tabelas_criar['values'] = tabelas
        self.dropdown_tabelas['values'] = tabelas
        self.dropdown_tabelas_atualizar['values'] = tabelas
        self.dropdown_tabelas_excluir['values'] = tabelas

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