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

  def create(self,tabela,colunas,valores):
    query = f"insert into {tabela} ({", ".join(colunas)}) values ({", ".join(valores)})"
    self.cursor.execute(query)
    self.db.commit()

  def __exit__(self):
    self.cursor.close()
    self.db.close()

parquebd = ParqueDB()
parquebd.create("Parque",["nome","endereco","horario_funcionamento"],["'Da cidade'","'Brasília'","'Toda hora'"])
