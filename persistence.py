import mysql.connector

class Database:
  def __init__(self,dbname,dbuser="admin",dbpasswd="admin"):
    self.db = mysql.connector.connect(
      host="localhost",
      user=dbuser,
      passwd=dbpasswd,
      database=dbname
    )
    self.cursor = self.db.cursor()

  def executeQuery(self,query,params=None):
    if params:
      self.cursor.execute(query,params)
      self.db.commit()
      return
    self.cursor.execute(query)
    self.db.commit()

  def insertTable(self,tabela,dados):
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
    return self.executeQuery(query,values)

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
    return self.executeQuery(query,values+identifiers)

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
    return self.executeQuery(query,identifiers)

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

class ParqueBD:
  def __init__(self):
    self.db = Database("gestao_parques")

  def createUser(self,nome,cpf,email):
    return self.db.insertTable("Usuario",{"nome_completo":nome,"cpf":cpf,"email":email})
  
  def readUser(self,userID=None,name=None,cpf=None,email=None):
    if (not userID) and ((not name) or (not cpf) or (not email)):
      return "Identifique o usuario pelo ID ou atributos"

    if name and cpf and email:
      return self.db.readTable("Usuario",filtros={"nome_completo":name,"cpf":cpf,"email":email})
    return self.db.readTable("Usuario",filtros={"id_usuario":userID})
  
  def updtUser(self,userID=None,name=None,cpf=None,email=None,newname=None,newcpf=None,newemail=None):
    if (not userID) and ((not name) or (not cpf) or (not email)):
      return "Identifique o usuario pelo ID ou atributos"
    
    # Prioriza identificar por nome cpf e email para
    # permitir uma insercao mais simples passando ID aleatorio
    if name and cpf and email:
      identificadores = {"nome_completo":name,"cpf":cpf,"email":email}
    else:
      identificadores = {"id_usuario":userID}

    invalid = 0 # se os tres campos forem vazios nao ha o que atualizar
    novos_valores = {}
    if newname:
      novos_valores["nome_completo"] = newname
      invalid += 1
    if newcpf:
      novos_valores["cpf"] = newcpf
      invalid += 1
    if newemail:
      novos_valores["email"] = newemail
      invalid += 1
    if invalid < 1:
      return "Altere pelo menos um valor"
    
    return self.db.updateTable("Usuario",novos_valores,identificadores)
  
  def deleteUser(self,userID=None,name=None,cpf=None,email=None):
    if (not userID) and ((not name) or (not cpf) or (not email)):
      return "Identifique o usuario pelo ID ou atributos"

    if name and cpf and email:
      return self.db.deleteTable("Usuario",{"nome_completo":name,"cpf":cpf,"email":email})
    return self.db.deleteTable("Usuario",{"id_usuario":userID})

mybd = ParqueBD()
# print(mybd.createUser("Claudio","00000000001","claudio@fake.com"))
# print(mybd.readUser("1"))
# print(mybd.readUser("-1","Claudio","00000000001","claudio2@fake.com"))
# print(mybd.updtUser(userID="1",newemail="claudio3@fake.com"))
# print(mybd.updtUser("-1","Claudio","00000000001","claudio3@fake.com",newemail="claudio2@fake.com"))
# print(mybd.deleteUser("1"))
# print(mybd.createUser("Irmao do Claudio","00000000002","claudiobrother@fake.com"))
# print(mybd.readUser("1"))
# print(mybd.readUser("2"))
# print(mybd.deleteUser("-1","Irmao do Claudio","00000000002","claudiobrother@fake.com"))
