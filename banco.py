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

  def __del__(self):
    self.banco.quitDB()
