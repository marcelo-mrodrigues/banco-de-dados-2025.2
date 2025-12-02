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

  def create(self,tabela,dados):
    # -- Dados é um dicionário dos valores desejados
    # Chave é o nome da coluna
    # Valor é o valor a ser inserido
    # Por exemplo: {"nome":"'Da cidade'","endereco":"'Brasília'","horario_funcionamento":"'Todo dia'"})
    colunas = []
    valores = []
    for key in dados:
      colunas.append(key)
      valores.append(dados[key])
    
    query = f"insert into {tabela} ({", ".join(colunas)}) values ({", ".join(valores)})"
    self.execute(query)

  def read(self, tabela, colunas=["*"], filtros=None):
    # -- Colunas é uma lista de strings com as colunas desejadas
    # Por exemplo: ["nome","endereco"]
    # -- Filtros é um dicionário com os filtros desejados
    # Por exemplo: {"id_parque":"1","nome":"'Parque do apenas um show'"}
    query = f"select {", ".join(colunas)} from {tabela}"

    if filtros:
      filters = []
      for key in filtros:
        filters.append(key + " = " + filtros[key])
      query += " where " + " and ".join(filters)

    self.cursor.execute(query)
    return self.cursor.fetchall()

  def update(self,tabela,novos_valores,identificadores):
    # -- Novos_valores deverá ser um dicionário
    # Chave é o nome da coluna
    # Valor é o valor a ser alterado
    # Por exemplo: {"nome":"'Parque do apenas um show'"}
    # -- Identificador também deverá ser um dicionário
    # Chave é o nome da coluna
    # Valor é o valor a ser identificado
    # Por exemplo: {"id_parque":"1"}

    if not identificadores:
      # Evitar de atualizar a base de dados inteira
      return

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

# Exemplos de create
# parquebd.create("Parque",{"nome":"'Da cidade'","endereco":"'Brasília'","horario_funcionamento":"'Todo dia'"})
# parquebd.create("Parque",{"nome":"'Do apenas um show'","endereco":"'Cartoon Network'","horario_funcionamento":"'Fechado'"})

# Exemplo de update
# parquebd.create("Parque",{"nome":"'NOME ERRADO'","endereco":"'ENDERECO ERRADO'","horario_funcionamento":"'ERRADO'"})
# parquebd.update("Parque",{"nome":"'Nome certo'","endereco":"'Endereco certo'","horario_funcionamento":"'Seg a Seg: 12:00 - 22:00'"},{"id_parque":"3"})

# Exemplos de read
# [[print(x) for x in parquebd.read("Parque")]]
# [[print(x) for x in parquebd.read("Parque",["nome"])]]
# [[print(x) for x in parquebd.read("Parque",["nome"],{"nome":"'Da cidade'","id_parque":"1"})]]
