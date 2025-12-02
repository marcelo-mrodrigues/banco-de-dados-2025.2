import mysql.connector

class ParqueDB:
  def __init__(self):
    self.db = mysql.connector.connect(
      host="localhost",
      user="admin",
      passwd="admin",
      database="gestao_parques"
    )
    self.cursor = self.db.cursor()

  def execute(self,query):
    self.cursor.execute(query)
    self.db.commit()

  def create(self,tabela,colunas,valores):
    # Ao passar strings é necessário usar aspas dentro das aspas, por exemplo:
    # "'Bob'"
    query = f"insert into {tabela} ({", ".join(colunas)}) values ({", ".join(valores)})"
    self.execute(query)

  def update(self,tabela,colunas,valores,identificador):
    # Identificador deverá ser uma tupla (ou lista), por exemplo:
    # ("id_parque","1")
    # ("nome","'Alice'")
    formated = []
    i = 0
    while i < len(colunas):
      formated.append(colunas[i] + " = " + valores[i])
      i += 1
    
    query = f"update {tabela} set {", ".join(formated)} where {identificador[0]} = {identificador[1]}"
    self.execute(query)

  def __exit__(self):
    self.cursor.close()
    self.db.close()

parquebd = ParqueDB()
parquebd.create("Parque",["nome","endereco","horario_funcionamento"],["'Da cidade'","'Brasília'","'Toda hora'"])
parquebd.update("Parque",["horario_funcionamento"],["'Quase toda hora'"],("id_parque","1"))
