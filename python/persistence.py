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

  def update(self,tabela,novos_valores,identificadores):
    # -- Novos_valores deverá ser um dicionário
    # Chave é o nome da coluna
    # Valor é o valor a ser alterado
    # Por exemplo: {"horario_funcionamento":"'Quase toda hora'"}
    # -- Identificador também deverá ser um dicionário
    # Chave é o nome da coluna
    # Valor é o valor a ser identificado
    # Por exemplo: {"nome":"'Parque do apenas um show'"}
    values = []
    for key in novos_valores:
      values.append(key + " = " + novos_valores[key])

    identifiers = []
    for key in identificadores:
      identifiers.append(key + " = " + identificadores[key])
    
    query = f"update {tabela} set {", ".join(values)} where {" AND ".join(identifiers)}"
    self.execute(query)

  def __exit__(self):
    self.cursor.close()
    self.db.close()

parquebd = ParqueDB()
