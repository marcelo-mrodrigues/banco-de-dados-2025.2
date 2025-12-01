create database gestao_parques;
use gestao_parques;

create table Parque(
	id_parque int primary key auto_increment,
    
    nome varchar(30),
    endereco varchar(50),
    horario_funcionamento varchar(50), -- timestamp seria muito especifico
    mapa_pdf blob
);

create table Evento(
	id_evento int primary key auto_increment,
    
    id_parque int not null,
    foreign key (id_parque) references Parque(id_parque),
    
    nome_evento varchar(30),
    inicio datetime,
    organizador varchar(30)
);

create table Usuario(
	id_usuario int primary key auto_increment,
    
    nome_completo varchar(30),
    cpf int not null unique,
    email varchar(30),
    telefone char(15) -- "(00) 12345-6789" = 15 char
);

create table Avaliacao(
	id_avaliacao int primary key auto_increment,
    
    id_parque int not null,
    foreign key (id_parque) references Parque(id_parque),
    id_usuario int not null,
    foreign key (id_usuario) references Usuario(id_usuario),
    
    nota enum('1','2','3','4','5'),
    comentario tinytext,
    data_avaliacao date
);

create table Funcionario(
    id_funcionario int primary key auto_increment,
    nome_completo varchar(30),
    matricula int unique,
    foto_perfil mediumblob
);

create table Cargo(
    id_cargo int primary key auto_increment,
    nome_cargo varchar(15),
    descricao tinytext
);

create table Alocacao(
    id_funcionario int not null,
    foreign key (id_funcionario) references Funcionario(id_funcionario),
    id_parque int not null,
    foreign key (id_parque) references Parque(id_parque),
    id_cargo int not null,
    foreign key (id_cargo) references Cargo(id_cargo),

    data_inicio date
);

create table Tipo_manutencao(
    id_tipo_manutencao int primary key auto_increment,
    nome_tipo varchar(30)
);

create table Tipo_equipamento(
    id_tipo_equipamento int primary key auto_increment,
    nome_tipo varchar(30),
    permite_reserva bool
);

create table Equipamento(
    id_equipamento int primary key auto_increment,

    id_parque int not null,
    foreign key (id_parque) references Parque(id_parque),
    id_tipo_equipamento int not null,
    foreign key (id_tipo_equipamento) references Tipo_equipamento(id_tipo_equipamento),

    nome_equipamento varchar(15),
    status_conservacao enum('Funcional','Em manutenção','Manutenção agendada','Quebrado','Desconhecido')
);

create table Ordem_servico(
    id_ordem_servico int primary key auto_increment,

    id_equipamento int not null,
    foreign key (id_equipamento) references Equipamento(id_equipamento),
    id_tipo_manutencao int not null,
    foreign key (id_tipo_manutencao) references Tipo_manutencao(id_tipo_manutencao),
    id_funcionario_responsavel int not null,
    foreign key (id_funcionario_responsavel) references Funcionario(id_funcionario),

    data_abertura date,
    descricao_problema text,
    status_ordem enum('Pendente','Concluída','Cancelada')
);

create table Reserva(
    id_reserva int,

    id_usuario int not null,
    foreign key (id_usuario) references Usuario(id_usuario),
    id_equipamento int not null,
    foreign key (id_equipamento) references Equipamento(id_equipamento),

    inicio datetime not null,
    fim datetime not null,

    constraint id_reserva primary key (id_usuario, id_equipamento, inicio, fim)
);

drop database gestao_parques;
