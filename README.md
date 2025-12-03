# Projeto de Banco de Dados 2025.2
## Integrantes do grupo
Marcelo Marques Rodrigues - 221018960

Daniel Toledo Dantas - 211068477

## Especificações
Linguagem de programação: Python

SGBD utilizado: MySQL

## Onde IA foi usada
- Para criar uma foto de funcionário
- Para criar uma base para os cruds de funcionario baseado nos cruds de usuário e parque. Foram feitas alterações e revisões humanas

## Tutoriais
### MySQL connector
Utilizamos o ambiente virtual `projeto_bd`, para mudar para ele no linux basta rodar o seguinte comando na pasta principal:

```
source projeto_bd/bin/activate
```

Para sair do ambiente basta usar o comando: `deactivate`

### Criando usuario
O script que gerou o usuário padrão utilizado pelo banco de dados é o seguinte:

```sql
-- Codigo inicialmente gerado por IA e modificado posteriormente

-- Create the user
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'admin';

-- Grant full access
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'localhost' WITH GRANT OPTION;

-- Apply changes
FLUSH PRIVILEGES;

-- Exit MySQL
EXIT;
```
