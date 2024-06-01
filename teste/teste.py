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
   



class Aplicacao(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(fill="both", expand=True)

        self.master.title("Interface CRUD")
        self.master.geometry("1000x700")

        self.style = ttkthemes.ThemedStyle(self)
        self.style.set_theme("equilux")  # Use a theme that looks like MySQL Workbench

        self.db = ConectarDB()

        # Configurando o Notebook para ter abas no topo com ícones
        self.notebook = ttk.Notebook(self, style='TNotebook')
        self.notebook.pack(fill="both", expand=True)

        self.frames = {}
        self.icons = {
            "Importar/Exportar": "icons/import_export.png",
            "Criar": "icons/create.png",
            "Ler": "icons/read.png",
            "Atualizar": "icons/update.png",
            "Excluir": "icons/delete.png",
            "Nova Tabela": "icons/new_table.png",
            "Editor SQL": "icons/sql_editor.png"
        }

        for tab in ["Importar/Exportar", "Criar", "Ler", "Atualizar", "Excluir", "Nova Tabela", "Editor SQL"]:
            frame = ttk.Frame(self.notebook)
            frame.pack(fill="both", expand=True)
            icon = tk.PhotoImage(file=self.icons[tab])
            self.notebook.add(frame, text=tab, image=icon, compound=tk.LEFT)
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
        frame.config(padding=(20, 10))

        ttk.Label(frame, text="Nome da Tabela:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
        self.nome_tabela = ttk.Entry(frame, font=("Arial", 12))
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

        ttk.Label(frame_coluna, text=f"Coluna {row+1}", font=("Arial", 10)).grid(row=0, column=0, padx=10, pady=5)
        entrada_coluna = ttk.Entry(frame_coluna)
        entrada_coluna.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(frame_coluna, text="Tipo", font=("Arial", 10)).grid(row=0, column=2, padx=10, pady=5)
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

    def tab_importar_exportar(self):
        frame = self.frames["Importar/Exportar"]
        frame.config(padding=(20, 10))

        ttk.Label(frame, text="Selecione a Tabela:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
        self.lista_tabelas_importar_exportar = tk.StringVar()
        self.dropdown_tabelas_importar_exportar = ttk.Combobox(frame, textvariable=self.lista_tabelas_importar_exportar, font=("Arial", 12))
        self.dropdown_tabelas_importar_exportar.grid(row=0, column=1, padx=10, pady=10)
        self.dropdown_tabelas_importar_exportar['values'] = self.db.listar_tabelas()

        self.botao_atualizar_importar_exportar = ttk.Button(frame, text="Atualizar", command=self.atualizar_listas_tabelas)
        self.botao_atualizar_importar_exportar.grid(row=0, column=2, padx=10, pady=10)

        self.botao_exportar = ttk.Button(frame, text="Exportar", command=self.exportar_tabela)
        self.botao_exportar.grid(row=1, column=0, padx=10, pady=10)

        self.botao_importar = ttk.Button(frame, text="Importar", command=self.importar_tabela)
        self.botao_importar.grid(row=1, column=1, padx=10, pady=10)

    def tab_criar(self):
        frame = self.frames["Criar"]
        frame.config(padding=(20, 10))

        ttk.Label(frame, text="Selecione a Tabela:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
        self.lista_tabelas_criar = tk.StringVar()
        self.dropdown_tabelas_criar = ttk.Combobox(frame, textvariable=self.lista_tabelas_criar, font=("Arial", 12))
        self.dropdown_tabelas_criar.grid(row=0, column=1, padx=10, pady=10)
        self.dropdown_tabelas_criar['values'] = self.db.listar_tabelas()
        self.dropdown_tabelas_criar.bind("<<ComboboxSelected>>", self.atualizar_formulario_criar)

        self.entries_criar = []

    def tab_ler(self):
        frame = self.frames["Ler"]
        frame.config(padding=(20, 10))

        self.frame_checkbuttons = ttk.Frame(frame)
        self.frame_checkbuttons.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.frame_tabelas = ttk.Frame(frame)
        self.frame_tabelas.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.botao_atualizar_checkbuttons = ttk.Button(frame, text="Atualizar", command=self.atualizar_checkbuttons)
        self.botao_atualizar_checkbuttons.grid(row=1, column=0, padx=10, pady=10)

        self.botao_mostrar_tabelas = ttk.Button(frame, text="Mostrar Tabelas", command=self.mostrar_tabelas_selecionadas)
        self.botao_mostrar_tabelas.grid(row=1, column=1, padx=10, pady=10)

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        self.checkbuttons = []
    def tab_atualizar(self):
        frame = self.frames["Atualizar"]
        frame.config(padding=(20, 10))

        ttk.Label(frame, text="Selecione a Tabela:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
        self.lista_tabelas_atualizar = tk.StringVar()
        self.dropdown_tabelas_atualizar = ttk.Combobox(frame, textvariable=self.lista_tabelas_atualizar, font=("Arial", 12))
        self.dropdown_tabelas_atualizar.grid(row=0, column=1, padx=10, pady=10)
        self.dropdown_tabelas_atualizar['values'] = self.db.listar_tabelas()
        self.dropdown_tabelas_atualizar.bind("<<ComboboxSelected>>", self.atualizar_formulario_atualizar)

        self.entries_atualizar = []

    def tab_excluir(self):
        frame = self.frames["Excluir"]
        frame.config(padding=(20, 10))

        ttk.Label(frame, text="Selecione a Tabela:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
        self.lista_tabelas_excluir = tk.StringVar()
        self.dropdown_tabelas_excluir = ttk.Combobox(frame, textvariable=self.lista_tabelas_excluir, font=("Arial", 12))
        self.dropdown_tabelas_excluir.grid(row=0, column=1, padx=10, pady=10)
        self.dropdown_tabelas_excluir['values'] = self.db.listar_tabelas()
        self.dropdown_tabelas_excluir.bind("<<ComboboxSelected>>", self.atualizar_formulario_excluir)

        self.entries_excluir = []

    def tab_editor_sql(self):
        frame = self.frames["Editor SQL"]
        frame.config(padding=(20, 10))

        self.texto_editor_sql = tk.Text(frame, font=("Arial", 12), wrap="none")
        self.texto_editor_sql.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.frame_botoes_sql = ttk.Frame(frame)
        self.frame_botoes_sql.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.botao_executar_sql = ttk.Button(self.frame_botoes_sql, text="Executar SQL", command=self.executar_sql)
        self.botao_executar_sql.grid(row=0, column=0, padx=10, pady=10)

        self.botao_limpar_sql = ttk.Button(self.frame_botoes_sql, text="Limpar", command=self.limpar_sql)
        self.botao_limpar_sql.grid(row=0, column=1, padx=10, pady=10)

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

    def executar_sql(self):
        query = self.texto_editor_sql.get("1.0", "end-1c")
        try:
            self.db.cur.execute(query)
            self.db.con.commit()
            resultado = self.db.cur.fetchall()
            messagebox.showinfo("Sucesso", f"Query executada com sucesso.\nResultado:\n{resultado}")
        except Error as e:
            messagebox.showerror("Erro de SQL", f"Falha ao executar query: {e}")

    def limpar_sql(self):
        self.texto_editor_sql.delete("1.0", "end")

    def atualizar_listas_tabelas(self):
        tabelas = self.db.listar_tabelas()
        self.dropdown_tabelas_importar_exportar['values'] = tabelas
        self.dropdown_tabelas_criar['values'] = tabelas
        self.dropdown_tabelas_atualizar['values'] = tabelas
        self.dropdown_tabelas_excluir['values'] = tabelas

    def atualizar_formulario_criar(self, event):
        tabela = self.lista_tabelas_criar.get()
        self.entries_criar = self.db.get_columns(tabela)
        self.mostrar_formulario(self.frames["Criar"], self.entries_criar)

    def atualizar_formulario_atualizar(self, event):
        tabela = self.lista_tabelas_atualizar.get()
        self.entries_atualizar = self.db.get_columns(tabela)
        self.mostrar_formulario(self.frames["Atualizar"], self.entries_atualizar)

    def atualizar_formulario_excluir(self, event):
        tabela = self.lista_tabelas_excluir.get()
        self.entries_excluir = self.db.get_columns(tabela)
        self.mostrar_formulario(self.frames["Excluir"], self.entries_excluir)

    def mostrar_formulario(self, frame, entries):
        for widget in frame.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.destroy()
        
        for idx, (nome_coluna, tipo_coluna) in enumerate(entries):
            ttk.Label(frame, text=nome_coluna, font=("Arial", 12)).grid(row=idx+1, column=0, padx=10, pady=10)
            entrada = ttk.Entry(frame, font=("Arial", 12))
            entrada.grid(row=idx+1, column=1, padx=10, pady=10)

    def mostrar_tabelas_selecionadas(self):
        tabelas_selecionadas = [cb.get("text") for cb in self.checkbuttons if cb.var.get()]
        resultado = ""
        for tabela in tabelas_selecionadas:
            self.db.cur.execute(f"SELECT * FROM {tabela}")
            resultado += f"Tabela: {tabela}\n"
            resultado += str(self.db.cur.fetchall()) + "\n\n"
        messagebox.showinfo("Tabelas Selecionadas", resultado)

    def atualizar_checkbuttons(self):
        for widget in self.frame_checkbuttons.winfo_children():
            widget.destroy()

        self.checkbuttons = []
        for idx, tabela in enumerate(self.db.listar_tabelas()):
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.frame_checkbuttons, text=tabela, variable=var)
            cb.var = var
            cb.grid(row=idx, column=0, padx=10, pady=5, sticky="w")
            self.checkbuttons.append(cb)

    def exportar_tabela(self):
        tabela = self.lista_tabelas_importar_exportar.get()
        if not tabela:
            messagebox.showwarning("Erro de Seleção", "Por favor, selecione uma tabela para exportar.")
            return

        arquivo = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not arquivo:
            return

        try:
            self.db.exportar_tabela(tabela, arquivo)
            messagebox.showinfo("Sucesso", f"Tabela {tabela} exportada com sucesso para {arquivo}")
        except Error as e:
            messagebox.showerror("Erro de Exportação", f"Falha ao exportar tabela: {e}")

    def importar_tabela(self):
        arquivo = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not arquivo:
            return

        tabela = self.lista_tabelas_importar_exportar.get()
        if not tabela:
            tabela = os.path.splitext(os.path.basename(arquivo))[0]

        try:
            self.db.importar_tabela(arquivo, tabela)
            self.atualizar_listas_tabelas()
            messagebox.showinfo("Sucesso", f"Tabela importada com sucesso de {arquivo}")
        except Error as e:
            messagebox.showerror("Erro de Importação", f"Falha ao importar tabela: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacao(master=root)
    app.mainloop()