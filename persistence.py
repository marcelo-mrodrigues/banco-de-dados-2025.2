import mysql.connector

class Database:
  def __init__(self,dbhost,dbname,dbuser,dbpasswd):
    self.db = mysql.connector.connect(
      host=dbhost,
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

  def quitConnection(self):
    self.cursor.close()
    self.db.close()

class ParqueBD:
  def __init__(self):
    self.db = Database("localhost","gestao_parques","admin","admin")

  def quitDB(self):
    self.db.quitConnection()

  # -- CRUD Parque --
  def createPark(self,name,address=None,parkshift=None,mappath=None):
    data = {"nome":name}
    if address:
      data["endereco"] = address
    if parkshift:
      data["horario_funcionamento"] = parkshift
    if mappath:
      data["mapa_pdf"] = self.db.openBlob(mappath)
    
    return self.db.insertTable("Parque",data)
  
  def readPark(self,parkID=-1,name=None,address=None,parkshift=None):
    if (parkID < 1) and (not name) and (not address) and (not parkshift):
      raise ValueError("Identifique o(s) parque(s) de alguma maneira")

    filters = {}
    if parkID > 0:
      filters["id_parque"] = parkID
    if name:
      filters["nome"] = name
    if address:
      filters["endereco"] = address
    if parkshift:
      filters["horario_funcionamento"] = parkshift

    return self.db.readTable("Parque",filtros=filters)
  
  def updtPark(self,parkID,newname=None,newaddress=None,newparkshift=None,newmappath=None): 
    if parkID < 1:
      raise ValueError("ID de parque invalido na atualizacao")

    invalid = 0 # se os tres campos forem vazios nao ha o que atualizar
    novos_valores = {}
    if newname:
      novos_valores["nome"] = newname
      invalid += 1
    if newaddress:
      novos_valores["endereco"] = newaddress
      invalid += 1
    if newparkshift:
      novos_valores["horario_funcionamento"] = newparkshift
      invalid += 1
    if newmappath:
      novos_valores["mapa_pdf"] = self.db.openBlob(newmappath)
      invalid += 1
    
    if invalid < 1:
      raise ValueError("Forneça ao menos um dado novo para atualizar o parque")
    
    return self.db.updateTable("Parque",novos_valores,{"id_parque":parkID})
  
  def deletePark(self,parkID):
    if parkID < 1:
      raise ValueError("ID de parque invalido na remoção")
    return self.db.deleteTable("Parque",{"id_parque":parkID})
  
  # -- CRUD Usuario --
  def createUser(self,name,cpf,email,telephone=None):
    data = {"nome_completo":name,"cpf":cpf,"email":email}
    if telephone:
      data["telefone"] = telephone
    
    return self.db.insertTable("Usuario",data)
  
  def readUser(self,userID=-1,name=None,cpf=None,email=None,telephone=None):
    if (userID < 1) and (not name) and (not cpf) and (not email) and (not telephone):
      raise ValueError("Identifique o(s) usuario(s) de alguma maneira")

    filters = {}
    if userID > 0:
      filters["id_usuario"] = userID
    if name:
      filters["nome_completo"] = name
    if cpf:
      filters["cpf"] = cpf
    if email:
      filters["email"] = email
    if telephone:
      filters["telefone"] = telephone

    return self.db.readTable("Usuario",filtros=filters)
  
  def updtUser(self,userID=-1,cpf=None,email=None,newname=None,newcpf=None,newemail=None,newtelephone=None):
    if (userID < 1) and (not cpf) and (not email):
      raise ValueError("Identifique o usuario pelo ID, cpf ou email")
    
    identificadores = {}
    if userID > 0:
      identificadores["id_usuario"] = userID
    if cpf:
      identificadores["cpf"] = cpf
    if email:
      identificadores["email"] = email

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
    if newtelephone:
      novos_valores["telefone"] = newtelephone
      invalid += 1
    
    if invalid < 1:
      raise ValueError("Forneça ao menos um dado novo para atualizar o usuario")
    
    return self.db.updateTable("Usuario",novos_valores,identificadores)
  
  def deleteUser(self,userID=-1,cpf=None,email=None):
    if (userID < 1) and (not cpf) and (not email):
      raise ValueError("Identifique o usuario pelo ID, cpf ou email")

    filters = {}
    if userID > 0:
      filters["id_usuario"] = userID
    if cpf:
      filters["cpf"] = cpf
    if email:
      filters["email"] = email

    return self.db.deleteTable("Usuario",filters)
  
  # -- CRUD Funcionario --
  # Gerado inicalmente por IA
  # Devidamente revisado por humano
  def createEmployee(self, name, registration, photopath=None):
    data = {"nome_completo": name, "matricula": registration}
    if photopath:
      data["foto_perfil"] = self.db.openBlob(photopath)
    
    return self.db.insertTable("Funcionario", data)

  def readEmployee(self, funcID=-1, name=None, registration=None):
    if (funcID < 1) and (not name) and (not registration):
      raise ValueError("Identifique o(s) funcionário(s) por ID, Nome ou Matrícula")

    filters = {}
    if funcID > 0:
      filters["id_funcionario"] = funcID
    if name:
      filters["nome_completo"] = name
    if registration:
      filters["matricula"] = registration

    return self.db.readTable("Funcionario", filtros=filters)

  def updtEmployee(self, funcID=-1, registration=None, newname=None, newregistration=None, newphotopath=None):
    if (funcID < 1) and (not registration):
      raise ValueError("Identifique o funcionário pelo ID ou Matrícula para atualizar")
    
    identificadores = {}
    if funcID > 0:
      identificadores["id_funcionario"] = funcID
    if registration:
      identificadores["matricula"] = registration

    invalid = 0
    novos_valores = {}
    if newname:
      novos_valores["nome_completo"] = newname
      invalid += 1
    if newregistration:
      novos_valores["matricula"] = newregistration
      invalid += 1
    if newphotopath:
      novos_valores["foto_perfil"] = self.db.openBlob(newphotopath)
      invalid += 1
    
    if invalid < 1:
      raise ValueError("Forneça ao menos um dado novo para atualizar o funcionario")
    
    return self.db.updateTable("Funcionario", novos_valores, identificadores)

  def deleteEmployee(self, funcID=-1, registration=None):
    if (funcID < 1) and (not registration):
      raise ValueError("Identifique o funcionário pelo ID ou Matrícula para remover")

    filters = {}
    if funcID > 0:
      filters["id_funcionario"] = funcID
    if registration:
      filters["matricula"] = registration

    return self.db.deleteTable("Funcionario", filters)

mybd = ParqueBD()
