import sqlite3

class Banco_dados:
  def __init__(self,nome):
    self.conexao = sqlite3.connect(nome)
    self.cursor = self.conexao.cursor()

  def getCursor(self):
    return self.cursor

  def getConexao(self):
    return self.conexao

  def addTable(self,tabela,atributos):
    # atributos devem ser passados como dicionário
    # as chaves são os nomes dos atributos e os valores suas propriedades
    estrutura = ''''''
    for atributo in atributos:
      estrutura += f"{atributo} {atributos[atributo]},\n"
    estrutura = estrutura[:-2] # remover ultima "," e "enter"

    self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {tabela} (\n{estrutura})''')

  def insertTable(self,tabela,dados):
    # dados devem ser passados como dicionario
    # as chaves são os nomes dos dados e os valores o dado em si
    atributos = ""
    valores = ""
    for dado in dados:
      atributos += dado + ","
      valores += dados[dado] + ","
    atributos = atributos[:-1]
    valores = valores[:-1]

    self.cursor.execute(f'''INSERT INTO {tabela} ({atributos}) VALUES ({valores})''')
    self.conexao.commit()

  def queryTable(self,tabela, coluna, condicao=""):
    if condicao:
      self.cursor.execute(f"SELECT {coluna} FROM {tabela} WHERE {condicao}")
      return self.cursor.fetchall()
    
    self.cursor.execute(f"SELECT {coluna} FROM {tabela}")
    return self.cursor.fetchall()

  def quitDB(self):
    self.conexao.close()
