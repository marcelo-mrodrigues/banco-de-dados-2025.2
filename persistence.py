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

  def executeQuery(self,query,params=None):
    if params:
      self.cursor.execute(query,params)
      self.db.commit()
      return
    self.cursor.execute(query)
    self.db.commit()

  def createTable(self,tabela,dados):
    # -- Dados é um dicionário dos valores desejados
    # Chave é o nome da coluna
    # Valor é o valor a ser inserido
    # Por exemplo: {"nome":"Da cidade","endereco":"Brasília","horario_funcionamento":"Todo dia"})
    columns = []
    values = []
    placeholders = []
    for key in dados:
      columns.append(key)
      values.append(dados[key])
      placeholders.append("%s")
    
    query = f"insert into {tabela} ({", ".join(columns)}) values ({", ".join(placeholders)})"
    self.execute(query,values)

  def readTable(self, tabela, colunas=["*"], filtros=None):
    # -- Colunas é uma lista de strings com as colunas desejadas
    # Por exemplo: ["nome","endereco"]
    # -- Filtros é um dicionário com os filtros desejados
    # Por exemplo: {"id_parque":"1","nome":"Parque do apenas um show"}
    query = f"select {", ".join(colunas)} from {tabela}"

    filters = []
    if filtros:
      placeholders = []
      for key in filtros:
        placeholders.append(key + " = %s")
        filters.append(filtros[key])
      query += " where " + " and ".join(placeholders)

    self.cursor.execute(query,filters)
    return self.cursor.fetchall()

  def updateTable(self,tabela,novos_valores,identificadores):
    # -- Novos_valores deverá ser um dicionário
    # Chave é o nome da coluna
    # Valor é o valor a ser alterado
    # Por exemplo: {"nome":"Parque do apenas um show"}
    # -- Identificador também deverá ser um dicionário
    # Chave é o nome da coluna
    # Valor é o valor a ser identificado
    # Por exemplo: {"id_parque":"1"}

    if not identificadores:
      # Evitar de atualizar a base de dados inteira
      return

    values = []
    value_placeholder = []
    for key in novos_valores:
      values.append(novos_valores[key])
      value_placeholder.append(key + " = %s")

    identifiers = []
    identifier_placeholder = []
    for key in identificadores:
      identifiers.append(identificadores[key])
      identifier_placeholder.append(key + " = %s")
    
    query = f"update {tabela} set {", ".join(value_placeholder)} where {" AND ".join(identifier_placeholder)}"
    self.execute(query,values+identifiers)

  def deleteTable(self,tabela,identificadores):
    # -- Identificador deverá ser um dicionário
    # Chave é o nome da coluna
    # Valor é o valor a ser identificado
    # Por exemplo: {"id_parque":"1"}

    if not identificadores:
      # Evitar de deletar a base de dados inteira
      return

    identifiers = []
    placeholders = []
    for key in identificadores:
      identifiers.append(identificadores[key])
      placeholders.append(key + " = %s")
    
    query = f"delete from {tabela} where {" AND ".join(placeholders)}"
    self.execute(query,identifiers)

  def openBlob(self,path):
    # Para salvar arquivos de outros tipos como pdf e/ou jpg
    with open(path, "rb") as file:
      # rb = abre o arquivo em modo binario
      return file.read()
    
  def reservar_procedure(self, id_usuario, id_equipamento, inicio, fim):
    try: #nova_rezerva
        args = (id_usuario, id_equipamento, inicio, fim)
        
        self.cursor.callproc('sp_nova_reserva', args)
        self.db.commit()
        print("Sucesso na reserva")
        return True
        
    except mysql.connector.Error as err:
        print(f"Erro ao reservar: {err}")
        return False


  def __exit__(self):
    self.cursor.close()
    self.db.close()
