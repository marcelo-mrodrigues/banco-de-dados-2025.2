import sqlite3

class Banco_dados:
  def __init__(self,nome):
    self.conexao = sqlite3.connect(nome + ".db")
    self.cursor = self.conexao.cursor()

  def getCursor(self):
    return self.cursor

  def getConexao(self):
    return self.conexao

  def addTable(self,tabela,atributos,chavesEstr={},pkComp=[],uniqueCnstr=[]):
    # atributos devem ser passados como dicionário
    # as chaves são os nomes dos atributos e os valores suas propriedades
    # chaves estrangeiras devem ser passadas como dicionário
    # as chaves são os nomes das tabelas que são referenciadas e o valores são as colunas
    # chaves primairas compostas recebem apenas a lista das colunas que a compoem
    
    estrutura = ''''''
    for atributo in atributos:
      estrutura += f"{atributo} {atributos[atributo]},\n"

    if chavesEstr:
      for fk in chavesEstr:
        estrutura += f"foreign key ({chavesEstr[fk]}) references {fk}({chavesEstr[fk]}),\n"
    
    if pkComp:
      estrutura += f"primary key ({", ".join(pkComp)}),\n"

    if uniqueCnstr:
        estrutura += f"CONSTRAINT unique_{tabela} UNIQUE ({", ".join(uniqueCnstr)}),\n"
    
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

class GestaoParques:
  def __init__(self):
    self.banco = Banco_dados("ParqueDB")
    self.conexao = self.banco.getConexao()
    self.cursor = self.banco.getCursor()

  def cria_tabelas_parque(self):
    self.banco.addTable("Parque",{
      "id_parque":"integer primary key autoincrement",
      "nome":"varchar(100) not null",
      "endereco":"varchar(255)",
      "horario_funcionamento":"varchar(100)",
      "mapa_pdf":"blob"
    })

    self.banco.addTable("Evento",{
      "id_evento":"integer primary key autoincrement",
      "id_parque":"integer not null",
      "nome_evento":"varchar(30) not null",
      "inicio":"datetime",
      "fim":"datetime",
      "organizador":"varchar(30)"},
      {"Parque":"id_parque"})
    
    self.banco.addTable("Usuario",{
      "id_usuario":"integer primary key autoincrement",
      "nome_completo":"varchar(150) not null",
      "cpf":"char(11) not null unique",
      "email":"varchar(100) not null unique",
      "telefone":"varchar(20)"
    })

    self.banco.addTable("Avaliacao",{
      "id_avaliacao":"integer primary key autoincrement",
      "id_parque":"integer not null",
      "id_usuario":"integer not null",
      "nota":"text check(nota in ('1','2','3','4','5'))",
      "comentario":"tinytext",
      "data_avaliacao":"date default current_date"
    },{"Parque":"id_parque","Usuario":"id_usuario"})

    self.banco.addTable("Funcionario",{
      "id_funcionario":"integer primary key autoincrement",
      "nome_completo":"varchar(30)",
      "matricula":"integer unique",
      "foto_perfil":"blob"
    })

    self.banco.addTable("Cargo",{
      "id_cargo":"integer primary key autoincrement",
      "nome_cargo":"varchar(30) not null",
      "descricao":"tinytext"
    })

    self.banco.addTable("Alocacao",{
      "id_funcionario":"integer not null",
      "id_parque":"integer not null",
      "id_cargo":"integer not null",
      "data_inicio":"date"
    },{"Funcionario":"id_funcionario","Parque":"id_parque","Cargo":"id_cargo"},["id_funcionario","id_parque"])
  
    self.banco.addTable("Tipo_manutencao",{
      "id_tipo_manutencao":"integer primary key autoincrement",
      "nome_tipo":"varchar(30) not null"
    })

    self.banco.addTable("Tipo_equipamento",{
      "id_tipo_equipamento":"integer primary key autoincrement",
      "nome_tipo":"varchar(30)",
      "permite_reserva":"bool default FALSE"
    })

    self.banco.addTable("Equipamento",{
      "id_equipamento":"integer primary key autoincrement",
      "id_parque":"integer not null",
      "id_tipo_equipamento":"integer not null",
      "nome_equipamento":"varchar(15)",
      "status_conservacao":"text check (status_conservacao in ('Funcional','Em manutenção','Manutenção agendada','Quebrado','Desconhecido'))",
    },{"Parque":"id_parque","Tipo_equipamento":"id_tipo_equipamento"})

    self.banco.addTable("Ordem_servico",{
      "id_ordem_servico":"integer primary key autoincrement",
      "id_equipamento":"integer not null",
      "id_tipo_manutencao":"integer not null",
      "id_funcionario":"integer not null", # alteracao pequena de nome
      "data_abertura":"date",
      "descricao_problema":"text",
      "status_ordem":"text check (status_ordem in ('Pendente','Concluída','Cancelada')) default 'Pendente'"
    },{"Equipamento":"id_equipamento","Tipo_manutencao":"id_tipo_manutencao","Funcionario":"id_funcionario"})

    self.banco.addTable("Reserva",{
      "id_reserva":"integer primary key autoincrement",
      "id_usuario":"integer not null",
      "id_equipamento":"integer not null",
      "inicio":"datetime not null",
      "fim":"datetime not null",
    },{"Usuario":"id_usuario","Equipamento":"id_equipamento"},uniqueCnstr=["id_usuario", "id_equipamento", "inicio", "fim"])

  def view_e_trigger(self):
    try:  #  View
      self.cursor.execute("drop view if exists vw_detalhes_reserva")
      self.cursor.execute(''' 
        create view vw_detalhes_reserva as
        select r.id_reserva, u.nome_completo as usuario, e.nome_equipamento, r.inicio, r.fim, e.status_conservacao
        from Reserva r
        join Usuario u on r.id_usuario = u.id_usuario
        join Equipamento e on r.id_equipamento = e.id_equipamento
      ''')
      #  Trigger
      self.cursor.execute("drop trigger if exists trg_valida_equipamentos")
      self.cursor.execute('''
        create trigger trg_valida_equipamentos
        before insert on Reserva
        begin select case when (select status_conservacao from Equipamento where 
        id_equipamento = new.id_equipamento) != 'Funcional' then 
        raise (abort, 'Equipamento não está funcional.')
        end; end; ''')
      self.conexao.commit()
    except Exception as erro:
      print("Erro ao criar elementos:", erro)

  def registrar_reserva_segura_procedure(self , id_usuario, id_equipamento, inicio, fim):
    try:
      query = f''' SELECT COUNT(*) FROM Reserva WHERE id_equipamento = {id_equipamento}
                  and (('{inicio}' < fim AND '{fim}' > inicio)) '''
      self.cursor.execute(query)
      conflito = self.cursor.fetchone()[0]

      if conflito > 0:
        print("Erro de conflito de horário, já existe uma reserva neste periodo")
        return False
      dados = {
            "id_usuario": str(id_usuario),
            "id_equipamento": str(id_equipamento),
            "inicio": f"'{inicio}'",
            "fim": f"'{fim}'"
        }
      self.banco.insertTable("Reserva", dados)
      print("Reserva registrada com sucesso.")
      return True
    except Exception as erro:
      print("Erro ao registrar reserva:", erro)
      return False

  def __del__(self):
    self.banco.quitDB()

parque = GestaoParques()
parque.cria_tabelas_parque()
