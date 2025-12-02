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
    

# --------------- popular banco ---------------
  def popular_banco(self):
    """
    Insere dados iniciais apenas se as tabelas estiverem vazias.
    Isso permite rodar o código várias vezes sem dar erro de duplicidade.
    """
    try:
        print("\n--- Iniciando População do Banco ---")

        # --- 1. PARQUES (Mantendo os 5 originais) ---
        # Verificamos se já tem registro. Se tiver (count > 0), pulamos.
        if not self.banco.queryTable("Parque", "count(*)")[0][0]:
            print("Inserindo Parques...")
            self.banco.insertTable("Parque", {"nome": "'Parque da Cidade'", "endereco": "'Asa Sul'", "horario_funcionamento": "'06:00-22:00'"})
            self.banco.insertTable("Parque", {"nome": "'Parque Olhos D agua'", "endereco": "'Asa Norte'", "horario_funcionamento": "'07:00-19:00'"})
            self.banco.insertTable("Parque", {"nome": "'Jardim Botanico'", "endereco": "'Lago Sul'", "horario_funcionamento": "'09:00-17:00'"})
            self.banco.insertTable("Parque", {"nome": "'Parque Aguas Claras'", "endereco": "'Aguas Claras'", "horario_funcionamento": "'06:00-22:00'"})
            self.banco.insertTable("Parque", {"nome": "'Parque do Guara'", "endereco": "'Guara II'", "horario_funcionamento": "'08:00-18:00'"})
        else:
            print("Tabela Parque já possui dados. Pulando inserção.")

        # --- 2. CARGOS ---
        if not self.banco.queryTable("Cargo", "count(*)")[0][0]:
            print("Inserindo Cargos...")
            cargos = [
                {"nome_cargo": "'Jardineiro'", "descricao": "'Cuida das plantas e paisagismo'"},
                {"nome_cargo": "'Seguranca'", "descricao": "'Vigilancia patrimonial e rondas'"},
                {"nome_cargo": "'Administrador'", "descricao": "'Gestao geral do parque'"},
                {"nome_cargo": "'Auxiliar de Limpeza'", "descricao": "'Limpeza de banheiros e areas comuns'"},
                {"nome_cargo": "'Eletricista'", "descricao": "'Manutencao de iluminacao e bombas'"},
                {"nome_cargo": "'Atendente'", "descricao": "'Atendimento ao publico no portao'"}
            ]
            for c in cargos: self.banco.insertTable("Cargo", c)

        # --- 3. USUARIOS (Aumentado para 10) ---
        if not self.banco.queryTable("Usuario", "count(*)")[0][0]:
            print("Inserindo Usuarios...")
            usuarios = [
                {"nome_completo": "'Ana Silva'", "cpf": "'11122233344'", "email": "'ana@email.com'", "telefone": "'61999990001'"},
                {"nome_completo": "'Bruno Costa'", "cpf": "'22233344455'", "email": "'bruno@email.com'", "telefone": "'61999990002'"},
                {"nome_completo": "'Carla Dias'", "cpf": "'33344455566'", "email": "'carla@email.com'", "telefone": "'61999990003'"},
                {"nome_completo": "'Daniel Souza'", "cpf": "'44455566677'", "email": "'daniel@email.com'", "telefone": "'61999990004'"},
                {"nome_completo": "'Elena Lima'", "cpf": "'55566677788'", "email": "'elena@email.com'", "telefone": "'61999990005'"},
                {"nome_completo": "'Fabio Junior'", "cpf": "'66677788899'", "email": "'fabio@email.com'", "telefone": "'61999990006'"},
                {"nome_completo": "'Gabriela Rocha'", "cpf": "'77788899900'", "email": "'gabi@email.com'", "telefone": "'61999990007'"},
                {"nome_completo": "'Hugo Boss'", "cpf": "'88899900011'", "email": "'hugo@email.com'", "telefone": "'61999990008'"},
                {"nome_completo": "'Igor Santos'", "cpf": "'99900011122'", "email": "'igor@email.com'", "telefone": "'61999990009'"},
                {"nome_completo": "'Julia Roberts'", "cpf": "'00011122233'", "email": "'julia@email.com'", "telefone": "'61999990010'"}
            ]
            for u in usuarios: self.banco.insertTable("Usuario", u)

        # --- 4. FUNCIONARIOS (Aumentado para 8, distribuídos) ---
        if not self.banco.queryTable("Funcionario", "count(*)")[0][0]:
            print("Inserindo Funcionarios...")
            funcionarios = [
                {"nome_completo": "'Joao Pedro'", "matricula": "1001"}, # Jardineiro P1
                {"nome_completo": "'Maria Clara'", "matricula": "1002"}, # Seguranca P1
                {"nome_completo": "'Pedro Henrique'", "matricula": "1003"}, # Admin P2
                {"nome_completo": "'Ana Paula'", "matricula": "1004"}, # Limpeza P3
                {"nome_completo": "'Carlos Eduardo'", "matricula": "1005"}, # Eletricista P4
                {"nome_completo": "'Roberto Justos'", "matricula": "1006"}, # Admin P1
                {"nome_completo": "'Luiza Mel'", "matricula": "1007"}, # Jardineiro P3
                {"nome_completo": "'Snoop Dogg'", "matricula": "1008"} # Seguranca P5
            ]
            for f in funcionarios: self.banco.insertTable("Funcionario", f)

        # --- 5. ALOCACAO (Vinculando funcionários aos parques) ---
        if not self.banco.queryTable("Alocacao", "count(*)")[0][0]:
            print("Inserindo Alocacoes...")
            alocacoes = [
                {"id_funcionario": "1", "id_parque": "1", "id_cargo": "1", "data_inicio": "'2023-01-01'"},
                {"id_funcionario": "2", "id_parque": "1", "id_cargo": "2", "data_inicio": "'2023-02-01'"},
                {"id_funcionario": "6", "id_parque": "1", "id_cargo": "3", "data_inicio": "'2023-01-15'"}, # 2 func no P1
                {"id_funcionario": "3", "id_parque": "2", "id_cargo": "3", "data_inicio": "'2023-03-01'"},
                {"id_funcionario": "4", "id_parque": "3", "id_cargo": "4", "data_inicio": "'2023-04-01'"},
                {"id_funcionario": "7", "id_parque": "3", "id_cargo": "1", "data_inicio": "'2023-04-10'"}, # 2 func no P3
                {"id_funcionario": "5", "id_parque": "4", "id_cargo": "5", "data_inicio": "'2023-05-01'"},
                {"id_funcionario": "8", "id_parque": "5", "id_cargo": "2", "data_inicio": "'2023-06-01'"}
            ]
            for a in alocacoes: self.banco.insertTable("Alocacao", a)

        # --- 6. TIPOS (Equipamento e Manutenção) ---
        if not self.banco.queryTable("Tipo_equipamento", "count(*)")[0][0]:
            te = [
                {"nome_tipo": "'Quadra Esportiva'", "permite_reserva": "1"},
                {"nome_tipo": "'Churrasqueira'", "permite_reserva": "1"},
                {"nome_tipo": "'Playground'", "permite_reserva": "0"},
                {"nome_tipo": "'Banco de Praca'", "permite_reserva": "0"},
                {"nome_tipo": "'Academia Ar Livre'", "permite_reserva": "0"},
                {"nome_tipo": "'Bebedouro'", "permite_reserva": "0"}
            ]
            for t in te: self.banco.insertTable("Tipo_equipamento", t)

        if not self.banco.queryTable("Tipo_manutencao", "count(*)")[0][0]:
            tm = [
                {"nome_tipo": "'Preventiva'"}, {"nome_tipo": "'Corretiva'"},
                {"nome_tipo": "'Limpeza'"}, {"nome_tipo": "'Pintura'"}, {"nome_tipo": "'Eletrica'"}
            ]
            for t in tm: self.banco.insertTable("Tipo_manutencao", t)

        # --- 7. EQUIPAMENTOS (Mais itens e status variados) ---
        if not self.banco.queryTable("Equipamento", "count(*)")[0][0]:
            print("Inserindo Equipamentos...")
            equips = [
                # Parque 1
                {"id_parque": "1", "id_tipo_equipamento": "1", "nome_equipamento": "'Quadra Tenis A'", "status_conservacao": "'Funcional'"},
                {"id_parque": "1", "id_tipo_equipamento": "1", "nome_equipamento": "'Quadra Futsal'", "status_conservacao": "'Em manutenção'"},
                {"id_parque": "1", "id_tipo_equipamento": "2", "nome_equipamento": "'Quiosque 01'", "status_conservacao": "'Funcional'"},
                {"id_parque": "1", "id_tipo_equipamento": "6", "nome_equipamento": "'Bebedouro Central'", "status_conservacao": "'Quebrado'"},
                # Parque 2
                {"id_parque": "2", "id_tipo_equipamento": "3", "nome_equipamento": "'Balanco Duplo'", "status_conservacao": "'Quebrado'"},
                {"id_parque": "2", "id_tipo_equipamento": "3", "nome_equipamento": "'Escorregador'", "status_conservacao": "'Funcional'"},
                # Parque 3
                {"id_parque": "3", "id_tipo_equipamento": "4", "nome_equipamento": "'Banco Jardim 1'", "status_conservacao": "'Funcional'"},
                {"id_parque": "3", "id_tipo_equipamento": "2", "nome_equipamento": "'Churrasqueira VIP'", "status_conservacao": "'Manutenção agendada'"},
                # Parque 4
                {"id_parque": "4", "id_tipo_equipamento": "5", "nome_equipamento": "'Barra Fixa'", "status_conservacao": "'Funcional'"},
                {"id_parque": "4", "id_tipo_equipamento": "1", "nome_equipamento": "'Quadra Basquete'", "status_conservacao": "'Funcional'"},
                # Parque 5
                {"id_parque": "5", "id_tipo_equipamento": "6", "nome_equipamento": "'Bebedouro Pista'", "status_conservacao": "'Funcional'"}
            ]
            for e in equips: self.banco.insertTable("Equipamento", e)

        # --- 8. RESERVAS (Testando horários) ---
        if not self.banco.queryTable("Reserva", "count(*)")[0][0]:
            print("Inserindo Reservas...")
            reservas = [
                # Quadra Tenis (Eq 1) - Funcional
                {"id_usuario": "1", "id_equipamento": "1", "inicio": "'2025-12-01 08:00:00'", "fim": "'2025-12-01 09:00:00'"},
                {"id_usuario": "2", "id_equipamento": "1", "inicio": "'2025-12-01 09:00:00'", "fim": "'2025-12-01 10:00:00'"},
                # Quiosque (Eq 3) - Funcional
                {"id_usuario": "3", "id_equipamento": "3", "inicio": "'2025-12-05 12:00:00'", "fim": "'2025-12-05 16:00:00'"},
                # Quadra Basquete (Eq 10) - Funcional
                {"id_usuario": "4", "id_equipamento": "10", "inicio": "'2025-12-02 18:00:00'", "fim": "'2025-12-02 20:00:00'"}
            ]
            for r in reservas: self.banco.insertTable("Reserva", r)

        # --- 9. EVENTOS ---
        if not self.banco.queryTable("Evento", "count(*)")[0][0]:
            eventos = [
                {"id_parque": "1", "nome_evento": "'Show Verao'", "organizador": "'Pref'", "inicio": "'2025-12-20 10:00'", "fim": "'2025-12-20 22:00'"},
                {"id_parque": "2", "nome_evento": "'Feira Bio'", "organizador": "'ONG'", "inicio": "'2025-12-15 08:00'", "fim": "'2025-12-15 14:00'"},
                {"id_parque": "1", "nome_evento": "'Corrida 5k'", "organizador": "'Esporte'", "inicio": "'2025-11-01 07:00'", "fim": "'2025-11-01 11:00'"},
            ]
            for ev in eventos: self.banco.insertTable("Evento", ev)
        
        # --- 10. AVALIACOES ---
        if not self.banco.queryTable("Avaliacao", "count(*)")[0][0]:
            avals = [
                {"id_parque": "1", "id_usuario": "1", "nota": "'5'", "comentario": "'Melhor parque da cidade'"},
                {"id_parque": "1", "id_usuario": "2", "nota": "'4'", "comentario": "'Muito bom, mas cheio'"},
                {"id_parque": "2", "id_usuario": "3", "nota": "'2'", "comentario": "'Brinquedos quebrados'"},
                {"id_parque": "3", "id_usuario": "4", "nota": "'5'", "comentario": "'Lindo paisagismo'"},
                {"id_parque": "4", "id_usuario": "5", "nota": "'3'", "comentario": "'Falta bebedouro'"}
            ]
            for a in avals: self.banco.insertTable("Avaliacao", a)

        # --- 11. ORDEM DE SERVICO (Crucial para o Trigger) ---
        if not self.banco.queryTable("Ordem_servico", "count(*)")[0][0]:
            print("Inserindo Ordens de Serviço...")
            os_list = [
                # Bebedouro Quebrado (Eq 4)
                {"id_equipamento": "4", "id_tipo_manutencao": "2", "id_funcionario": "1", "status_ordem": "'Pendente'", "descricao_problema": "'Nao sai agua'"},
                # Balanco Quebrado (Eq 5)
                {"id_equipamento": "5", "id_tipo_manutencao": "2", "id_funcionario": "3", "status_ordem": "'Pendente'", "descricao_problema": "'Corrente estourada'"},
                # Manutencao Quadra Futsal (Eq 2)
                {"id_equipamento": "2", "id_tipo_manutencao": "4", "id_funcionario": "1", "status_ordem": "'Pendente'", "descricao_problema": "'Pintura do piso desgastada'"}
            ]
            for os in os_list: self.banco.insertTable("Ordem_servico", os)

        print("--- População Concluída (Ou dados já existiam) ---")

    except Exception as e:
      print("Erro ao popular banco:", e)

  def __del__(self):
    self.banco.quitDB()

parque = GestaoParques()
parque.cria_tabelas_parque()
parque.popular_banco()
resultado = parque.cursor.execute("SELECT * FROM vw_detalhes_reserva").fetchall()
print("Reservas agendadas:", resultado)
