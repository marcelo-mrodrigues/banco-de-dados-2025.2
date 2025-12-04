import mysql.connector
import datetime

class Database:
  def __init__(self,dbhost,dbname,dbuser,dbpasswd):
    self.db = mysql.connector.connect(
      host=dbhost,
      user=dbuser,
      passwd=dbpasswd,
      database=dbname
    )
    self.cursor = self.db.cursor()

  def getCursor(self):
    return self.cursor
  
  def commitChanges(self):
    self.db.commit()

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
    
    query = f"insert into {tabela} ({', '.join(columns)}) values ({', '.join(placeholders)})"
    return self.executeQuery(query,values)

  def readTable(self, tabela, colunas=["*"], filtros=None):
    # -- Colunas é uma lista de strings com as colunas desejadas
    # Por exemplo: ["nome","endereco"]
    # -- Filtros é um dicionário com os filtros desejados
    # Por exemplo: {"id_parque":"1","nome":"Parque do apenas um show"}
    query = f"select {', '.join(colunas)} from {tabela}"

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
    
    query = f"update {tabela} set {', '.join(value_placeholder)} where {' AND '.join(identifier_placeholder)}"
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
    
    query = f"delete from {tabela} where {' AND '.join(placeholders)}"
    return self.executeQuery(query,identifiers)

  def openBlob(self,path):
    # Para salvar arquivos de outros tipos como pdf e/ou jpg
    with open(path, "rb") as file:
      # rb = abre o arquivo em modo binario
      return file.read()

  def quitConnection(self):
    self.cursor.close()
    self.db.close()

class ParqueBD:
  def __init__(self):
    self.db = Database("localhost","gestao_parques","admin","admin")

  def quitDB(self):
    self.db.quitConnection()

  def reservar_procedure(self, id_usuario, id_equipamento, inicio, fim):
    args = (id_usuario, id_equipamento, inicio, fim)
    self.db.getCursor().callproc('sp_nova_reserva', args)
    self.db.commitChanges()

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

  # -- CRUD Cargo --
  def createCargo(self, name, description=None):
    data = {"nome_cargo": name}
    if description:
      data["descricao"] = description
    
    return self.db.insertTable("Cargo", data)

  def readCargo(self, cargoID=-1, name=None):
    if (cargoID < 1) and (not name):
      raise ValueError("Identifique o(s) cargo(s) pelo ID ou Nome")

    filters = {}
    if cargoID > 0:
      filters["id_cargo"] = cargoID
    if name:
      filters["nome_cargo"] = name

    return self.db.readTable("Cargo", filtros=filters)

  def updtCargo(self, cargoID, newname=None, newdescription=None):
    invalid = 0 
    novos_valores = {}
    if newname:
      novos_valores["nome_cargo"] = newname
      invalid += 1
    if newdescription:
      novos_valores["descricao"] = newdescription
      invalid += 1
    
    if invalid < 1:
      raise ValueError("Forneça ao menos um dado novo para atualizar o cargo")
    
    return self.db.updateTable("Cargo", novos_valores, {"id_cargo": cargoID})

  def deleteCargo(self, cargoID):
    return self.db.deleteTable("Cargo", {"id_cargo": cargoID})
  
  # -- CRUD Tipo Manutencao --
  def createMaintType(self, name):
    return self.db.insertTable("Tipo_manutencao", {"nome_tipo": name})

  def readMaintType(self, typeID=-1, name=None):
    if (typeID < 1) and (not name):
      raise ValueError("Identifique o(s) tipo(s) de manutenção pelo ID ou nome")

    filters = {}
    if typeID > 0:
      filters["id_tipo_manutencao"] = typeID
    if name:
      filters["nome_tipo"] = name

    return self.db.readTable("Tipo_manutencao", filtros=filters)

  def updtMaintType(self, typeID, newname):   
    return self.db.updateTable("Tipo_manutencao", {"nome_tipo": newname}, {"id_tipo_manutencao": typeID})

  def deleteMaintType(self, typeID):
    return self.db.deleteTable("Tipo_manutencao", {"id_tipo_manutencao": typeID})

  # -- CRUD Tipo Equipamento --
  def createEquipType(self, name, allowreservation=False):
    data = {"nome_tipo": name, "permite_reserva": allowreservation}
    return self.db.insertTable("Tipo_equipamento", data)

  def readEquipType(self, typeID=-1, name=None):
    if (typeID < 1) and (not name):
      raise ValueError("Identifique o tipo de equipamento pelo ID ou nome")

    filters = {}
    if typeID > 0:
      filters["id_tipo_equipamento"] = typeID
    if name:
      filters["nome_tipo"] = name

    return self.db.readTable("Tipo_equipamento", filtros=filters)

  def updtEquipType(self, typeID, newname=None, newallowreservation=None):
    invalid = 0
    novos_valores = {}
    
    if newname:
      novos_valores["nome_tipo"] = newname
      invalid += 1
    if newallowreservation is not None:
      # Verificação explicita de None pois False é um valor válido para atualização
      novos_valores["permite_reserva"] = newallowreservation
      invalid += 1
      
    if invalid < 1:
      raise ValueError("Forneça ao menos um dado novo para atualizar o tipo de equipamento")

    return self.db.updateTable("Tipo_equipamento", novos_valores, {"id_tipo_equipamento": typeID})

  def deleteEquipType(self, typeID):
    return self.db.deleteTable("Tipo_equipamento", {"id_tipo_equipamento": typeID})
  
  # -- CRUD Evento --
  def createEvent(self, parkID, name, start=None, end=None, organizer=None):
    # start e end devem ser passadas no formato 'YYYY-MM-DD HH:MM:SS' ou objeto datetime
    # não confundir "data" de dados em ingles, com data de tempo
    if parkID < 1:
      raise ValueError("É necessário vincular o evento a um parque válido (ID > 0)")

    data = {"id_parque": parkID, "nome_evento": name}
    if start:
      data["inicio"] = start
    if end:
      data["fim"] = end
    if organizer:
      data["organizador"] = organizer
    
    return self.db.insertTable("Evento", data)

  def readEvent(self, eventID=-1, parkID=-1, name=None, start=None, end=None, organizer=None):
    # A busca por eventos é bem mais fléxivel do que as demais

    filters = {}
    if eventID > 0:
      filters["id_evento"] = eventID
    if parkID > 0:
      filters["id_parque"] = parkID
    if name:
      filters["nome_evento"] = name
    if start:
      filters["inicio"] = start
    if end:
      filters["fim"] = end
    if organizer:
      filters["organizador"] = organizer

    if len(filters) < 1:
      raise ValueError("É necessário pelo menos alguma informação para buscar por evento(s)")
    
    return self.db.readTable("Evento", filtros=filters)

  def updtEvent(self, eventID, newparkID=-1, newname=None, newstart=None, newend=None, neworganizer=None):
    invalid = 0
    novos_valores = {}
    if newparkID > 0:
      novos_valores["id_parque"] = newparkID
      invalid += 1
    if newname:
      novos_valores["nome_evento"] = newname
      invalid += 1
    if newstart:
      novos_valores["inicio"] = newstart
      invalid += 1
    if newend:
      novos_valores["fim"] = newend
      invalid += 1
    if neworganizer:
      novos_valores["organizador"] = neworganizer
      invalid += 1

    if invalid < 1:
      raise ValueError("Forneça ao menos um dado novo para atualizar o evento")

    return self.db.updateTable("Evento", novos_valores, {"id_evento": eventID})

  def deleteEvent(self, eventID):
    return self.db.deleteTable("Evento", {"id_evento": eventID})
  
  # -- CRUD Avaliacao --
  def createReview(self, parkID, userID, rating, comment=None, date=None):
    if (parkID < 1) or (userID < 1):
      raise ValueError("É necessário vincular a avaliação a um parque e usuário válidos")

    data = {"id_parque": parkID, "id_usuario": userID, "nota": rating}
    
    if comment:
      data["comentario"] = comment
    if date:
      data["data_avaliacao"] = date
    
    return self.db.insertTable("Avaliacao", data)

  def readReview(self, avaliacaoID=-1, parkID=-1, userID=-1,rating=None,date=None):
    filters = {}
    if avaliacaoID > 0:
      filters["id_avaliacao"] = avaliacaoID
    if parkID > 0:
      filters["id_parque"] = parkID
    if userID > 0:
      filters["id_usuario"] = userID
    if rating:
      filters["nota"] = rating
    if date:
      filters["data"] = date
    
    if len(filters) < 1:
      raise ValueError("Identifique a(s) avaliação(ões) pelo ID, parque, usuário, nota ou data")

    return self.db.readTable("Avaliacao", filtros=filters)

  def updtReview(self, avaliacaoID, newrating=None, newcomment=None):   
    invalid = 0
    novos_valores = {}
    if newrating:
      novos_valores["nota"] = newrating
      invalid += 1
    if newcomment:
      novos_valores["comentario"] = newcomment
      invalid += 1
    
    if invalid < 1:
      raise ValueError("Forneça ao menos um dado novo para atualizar a avaliação")

    return self.db.updateTable("Avaliacao", novos_valores, {"id_avaliacao": avaliacaoID})

  def deleteReview(self, avaliacaoID):
    return self.db.deleteTable("Avaliacao", {"id_avaliacao": avaliacaoID})
  
  # -- CRUD Alocacao --
  def createAllocation(self, funcID, parkID, cargoID, startDate=None):
    if (funcID < 1) or (parkID < 1) or (cargoID < 1):
      raise ValueError("É necessário informar IDs de funcionário, parque e cargo.")

    data = {"id_funcionario": funcID, "id_parque": parkID, "id_cargo": cargoID}
    if startDate:
      data["data_inicio"] = startDate
    
    return self.db.insertTable("Alocacao", data)

  def readAllocation(self, funcID=-1, parkID=-1, cargoID=-1):
    if (funcID < 1) and (parkID < 1) and (cargoID < 1):
      raise ValueError("Informe ao menos um atributo da alocação")

    filters = {}
    if funcID > 0:
      filters["id_funcionario"] = funcID
    if parkID > 0:
      filters["id_parque"] = parkID
    if cargoID > 0:
      filters["id_cargo"] = cargoID

    return self.db.readTable("Alocacao", filtros=filters)

  def updtAllocation(self, funcID, parkID, newCargoID=-1, newStartDate=-1):
    invalid = 0
    novos_valores = {}
    if newCargoID > 0:
      novos_valores["id_cargo"] = newCargoID
      invalid += 1
    if newStartDate:
      novos_valores["data_inicio"] = newStartDate
      invalid += 1
      
    if invalid < 1:
      raise ValueError("Forneça um novo cargo ou nova data para atualizar")

    return self.db.updateTable("Alocacao", novos_valores, {"id_funcionario": funcID,"id_parque": parkID})

  def deleteAllocation(self, funcID, parkID):
    return self.db.deleteTable("Alocacao", {"id_funcionario": funcID,"id_parque": parkID})
  
  # -- CRUD Equipamento --
  def createEquipment(self, parkID, typeID, name, status='Funcional'):
    # Status pode ser 'Funcional','Em manutenção','Manutenção agendada','Quebrado' ou 'Desconhecido'
    data = {"id_parque": parkID, "id_tipo_equipamento": typeID,"nome_equipamento":name, "status_conservacao": status}

    return self.db.insertTable("Equipamento", data)

  def readEquipment(self, equipID=-1, parkID=-1, typeID=-1, name=None, status=None):
    filters = {}
    if equipID > 0:
      filters["id_equipamento"] = equipID
    if parkID > 0:
      filters["id_parque"] = parkID
    if typeID > 0:
      filters["id_tipo_equipamento"] = typeID
    if name:
      filters["nome_equipamento"] = name
    if status:
      filters["status_conservacao"] = status

    # if not filters:
    # nao implementado caso queira listar TODOS os equipamentos

    return self.db.readTable("Equipamento", filtros=filters)

  def updtEquipment(self, equipID, newParkID=-1, newTypeID=-1, newName=None, newStatus=None):
    invalid = 0
    novos_valores = {}
    if newParkID > 0:
      novos_valores["id_parque"] = newParkID
      invalid += 1
    if newTypeID > 0:
      novos_valores["id_tipo_equipamento"] = newTypeID
      invalid += 1
    if newName:
      novos_valores["nome_equipamento"] = newName
      invalid += 1
    if newStatus:
      novos_valores["status_conservacao"] = newStatus
      invalid += 1
    
    if invalid < 1:
      raise ValueError("Forneça ao menos um dado novo para atualizar o equipamento")

    return self.db.updateTable("Equipamento", novos_valores, {"id_equipamento": equipID})

  def deleteEquipment(self, equipID):
    return self.db.deleteTable("Equipamento", {"id_equipamento": equipID})

  # -- CRUD Ordem de Serviço --
  def createServiceOrder(self, equipID, maintTypeID, funcID, openDate=None, description=None, status='Pendente'):
    # Status pode ser 'Pendente','Concluída' ou 'Cancelada'
    data = {"id_equipamento": equipID, "id_tipo_manutencao": maintTypeID, "id_funcionario_responsavel": funcID, "status_ordem": status}

    if openDate:
      data["data_abertura"] = openDate
    if description:
      data["descricao_problema"] = description

    return self.db.insertTable("Ordem_servico", data)

  def readServiceOrder(self, orderID=-1, equipID=-1, funcID=-1, status=None, openDate=None):
    filters = {}
    if orderID > 0:
      filters["id_ordem_servico"] = orderID
    if equipID > 0:
      filters["id_equipamento"] = equipID
    if funcID > 0:
      filters["id_funcionario_responsavel"] = funcID
    if status:
      filters["status_ordem"] = status
    if openDate:
      filters["data_abertura"] = openDate

    return self.db.readTable("Ordem_servico", filtros=filters)

  def updtServiceOrder(self, orderID, newEquipID=-1,newMaintType=-1, newFuncID=-1, newDesc=None, newStatus=None):
    invalid = 0
    novos_valores = {}
    if newEquipID > 0:
      novos_valores["id_equipamento"] = newEquipID
    if newMaintType > 0:
      novos_valores["id_tipo_manutencao"] = newMaintType
    if newFuncID > 0:
      novos_valores["id_funcionario_responsavel"] = newFuncID
      invalid += 1
    if newDesc:
      novos_valores["descricao_problema"] = newDesc
      invalid += 1
    if newStatus:
      novos_valores["status_ordem"] = newStatus
      invalid += 1

    if invalid < 1:
      raise ValueError("Forneça novos dados para atualizar a ordem de serviço")

    return self.db.updateTable("Ordem_servico", novos_valores, {"id_ordem_servico": orderID})

  def deleteServiceOrder(self, orderID):
    return self.db.deleteTable("Ordem_servico", {"id_ordem_servico": orderID})
  
  # -- CRUD Reserva --
  def createReservation(self, userID, equipID, start, end):
    # Utilizando a procedure 'sp_nova_reserva'
    return self.reservar_procedure(userID, equipID, start, end)

  def readReservation(self, reservID=-1, userID=-1, equipID=-1, start=None, end=None):
    filters = {}
    if reservID > 0:
      filters["id_reserva"] = reservID
    if userID > 0:
      filters["id_usuario"] = userID
    if equipID > 0:
      filters["id_equipamento"] = equipID
    if start:
      filters["inicio"] = start
    if end:
      filters["fim"] = end

    # if not filters:
    # nao implementado caso queira listar TODAS as reservas
    
    return self.db.readTable("Reserva", filtros=filters)

  def updtReservation(self, reservID, newEquipID=-1, newStart=None, newEnd=None):  
    invalid = 0
    novos_valores = {}
    if newEquipID > 0:
      novos_valores["id_equipamento"] = newEquipID
      invalid += 1
    if newStart:
      novos_valores["inicio"] = newStart
      invalid += 1
    if newEnd:
      novos_valores["fim"] = newEnd
      invalid += 1

    if invalid < 1:
      raise ValueError("Forneça ao menos um dado novo para atualizar a reserva")

    return self.db.updateTable("Reserva", novos_valores, {"id_reserva": reservID})

  def deleteReservation(self, reservID):
    return self.db.deleteTable("Reserva", {"id_reserva": reservID})

mybd = ParqueBD()
# mybd.createPark("De diversão","Paraíso","Apenas as sextas 00:00 - 23:59")
# mybd.createUser("João","00011100011","joao@teste.com","(11) 10000-0000")
# mybd.createUser("José","11100011100","jose@teste.com","(00) 01111-1111")
# mybd.createEquipType("Brinqudo",True)
# mybd.createEquipment(1,1,"Carrosell")
# # YYYY-MM-DD hh:mm:ss
# mybd.createReservation(2,1,"2024-01-01 00:00:00","2024-12-31 23:59:59")
# mybd.createReservation(1,1,"2025-01-01 00:00:00","2025-12-31 23:59:59")
# mybd.createReservation(2,1,"2026-01-01 00:00:00","2026-12-31 23:59:59")

# mybd.updtReservation(3,newEnd="2026-01-01 00:00:00") # erro esperado
