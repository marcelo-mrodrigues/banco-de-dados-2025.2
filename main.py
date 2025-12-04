import os
import sys
from persistence import ParqueBD


def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')


def pausar():
    input("\nPressione Enter para continuar...")


def ler_input_opcional(mensagem):
    valor = input(mensagem).strip()
    return valor if valor else None


def ler_int(mensagem):
    while True:
        valor = input(mensagem).strip()
        if not valor: return None
        try:
            return int(valor)
        except ValueError:
            print("Por favor, digite um numero valido.")

def imprimir_resultados(resultados, colunas=None):
    if not resultados:
        print("\nNenhum registro encontrado.")
        return

    print("-" * 50)
    if colunas:
        header = " | ".join(colunas)
        print(header)
        print("-" * len(header))

    for row in resultados:
        row_str = [str(item) for item in row]
        print(" | ".join(row_str))
    print("-" * 50)


def pedir_criterio_busca(entidade):
    print(f"\n--- Buscar {entidade} ---")
    print("1. Buscar por ID")
    print("2. Buscar por Nome exato")
    print("0. Cancelar")

    tipo = input("Escolha: ").strip()

    if tipo == '1':
        valor = ler_int("Digite o ID: ")
        return ("id", valor)
    elif tipo == '2':
        valor = input("Digite o Nome: ").strip()
        return ("nome", valor)
    else:
        return (None, None)


def menu_parque(bd):
    while True:
        print("GESTAO DE PARQUES")
        print("1. Criar Parque")
        print("2. Buscar Parque")
        print("3. Atualizar Parque")
        print("4. Deletar Parque")
        print("0. Voltar")

        opcao = input("\nEscolha: ")

        if opcao == '1':
            nome = input("Nome do Parque: ")
            end = ler_input_opcional("Endereco: ")
            horario = ler_input_opcional("Horario: ")
            try:
                bd.createPark(nome, end, horario)
                print("Sucesso: Parque criado!")
            except Exception as e:
                print(f"Erro: {e}")
            pausar()

        elif opcao == '2':
            print("\n--- Buscar Parque por: ---")
            print("1. ID")
            print("2. Nome")
            print("3. Endereco")
            print("4. Horario")
            tipo_busca = input("Escolha o filtro: ").strip()

            try:
                resultados = []
                if tipo_busca == '1':
                    val = ler_int("Digite o ID: ")
                    if val: resultados = bd.readPark(parkID=val)

                elif tipo_busca == '2':
                    val = input("Digite o Nome: ").strip()
                    if val: resultados = bd.readPark(name=val)

                elif tipo_busca == '3':
                    val = input("Digite o Endereco: ").strip()
                    if val: resultados = bd.readPark(address=val)

                elif tipo_busca == '4':
                    val = input("Digite o Horario: ").strip()
                    if val: resultados = bd.readPark(parkshift=val)

                else:
                    print("Opção invalida ou cancelada.")
                    pausar()
                    continue

                imprimir_resultados(resultados, ["ID", "Nome", "Endereco", "Horario", "Mapa"])

            except Exception as e:
                print(f"Erro na busca: {e}")
            pausar()

        elif opcao == '3':
            id_p = ler_int("ID do Parque a atualizar: ")
            if not id_p:
                print("ID Obrigatorio.")
                pausar()
                continue

            nome = ler_input_opcional("Novo Nome: ")
            end = ler_input_opcional("Novo Endereco: ")
            horario = ler_input_opcional("Novo Horario: ")

            try:
                bd.updtPark(id_p, newname=nome, newaddress=end, newparkshift=horario)
                print("Sucesso: Parque atualizado!")
            except Exception as e:
                print(f"Erro: {e}")
            pausar()

        elif opcao == '4':
            id_p = ler_int("ID do Parque a deletar: ")
            try:
                bd.deletePark(id_p)
                print("Sucesso: Parque removido!")
            except Exception as e:
                print(f"Erro: {e}")
            pausar()

        elif opcao == '0':
            break


def menu_usuario(bd):
    while True:
        print("GESTAO DE USUARIOS")
        print("1. Criar Usuario")
        print("2. Buscar Usuario")
        print("3. Atualizar Usuario")
        print("4. Deletar Usuario")
        print("0. Voltar")

        opcao = input("\nEscolha: ")

        if opcao == '1':
            nome = input("Nome Completo: ")
            cpf = input("CPF: ")
            email = input("Email: ")
            tel = ler_input_opcional("Telefone: ")
            try:
                bd.createUser(nome, cpf, email, tel)
                print("Sucesso: Usuario criado!")
            except Exception as e:
                print(f"Erro: {e}")
            pausar()

        elif opcao == '2':
            print("\n--- Buscar Usuario por: ---")
            print("1. ID")
            print("2. Nome")
            print("3. CPF")
            print("4. Email")
            print("5. Telefone")
            tipo_busca = input("Escolha o filtro: ").strip()

            try:
                resultados = []

                if tipo_busca == '1':
                    val = ler_int("Digite o ID: ")
                    if val: resultados = bd.readUser(userID=val)

                elif tipo_busca == '2':
                    val = input("Digite o Nome: ").strip()
                    if val: resultados = bd.readUser(name=val)

                elif tipo_busca == '3':
                    val = input("Digite o CPF: ").strip()
                    if val: resultados = bd.readUser(cpf=val)

                elif tipo_busca == '4':
                    val = input("Digite o Email: ").strip()
                    if val: resultados = bd.readUser(email=val)

                elif tipo_busca == '5':
                    val = input("Digite o Telefone: ").strip()
                    if val: resultados = bd.readUser(telephone=val)

                else:
                    print("Opcao invalida ou cancelada.")
                    pausar()
                    continue

                imprimir_resultados(resultados, ["ID", "Nome", "CPF", "Email", "Telefone"])

            except Exception as e:
                print(f"Erro na busca: {e}")
            pausar()

        elif opcao == '3':
            id_u = ler_int("ID do Usuario a atualizar: ")
            if not id_u:
                print("ID Obrigatorio")
                pausar()
                continue

            print("Preencha apenas o que deseja mudar:")
            nome = ler_input_opcional("Novo Nome: ")
            cpf = ler_input_opcional("Novo CPF: ")
            email = ler_input_opcional("Novo Email: ")
            tel = ler_input_opcional("Novo Telefone: ")

            try:
                bd.updtUser(userID=id_u, newname=nome, newcpf=cpf, newemail=email, newtelephone=tel)
                print("Sucesso: Usuario atualizado!")
            except Exception as e:
                print(f"Erro: {e}")
            pausar()

        elif opcao == '4':
            id_u = ler_int("ID do Usuario a deletar: ")
            try:
                bd.deleteUser(userID=id_u)
                print("Sucesso: Usuario deletado!")
            except Exception as e:
                print(f"Erro: {e}")
            pausar()

        elif opcao == '0':
            break


def menu_funcionario(bd):
    while True:
        print("GESTAO DE FUNCIONARIOS")
        print("1. Criar Funcionario")
        print("2. Buscar Funcionario")
        print("3. Atualizar Funcionario")
        print("4. Deletar Funcionario")
        print("0. Voltar")

        opcao = input("\nEscolha: ")

        if opcao == '1':
            nome = input("Nome: ")
            mat = input("Matricula: ")
            try:
                bd.createEmployee(nome, mat)
                print("Sucesso: Funcionario criado!")
            except Exception as e:
                print(f"Erro: {e}")
            pausar()

        elif opcao == '2':
            print("\n--- Buscar por: ---")
            print("1. ID")
            print("2. Nome")
            print("3. Matricula")
            tipo_busca = input("Escolha o filtro: ").strip()

            try:
                resultados = []
                if tipo_busca == '1':
                    id_f = ler_int("Digite o ID: ")
                    if id_f: resultados = bd.readEmployee(funcID=id_f)

                elif tipo_busca == '2':
                    nome = input("Digite o Nome (exato): ").strip()
                    if nome: resultados = bd.readEmployee(name=nome)

                elif tipo_busca == '3':
                    mat = input("Digite a Matricula: ").strip()
                    if mat: resultados = bd.readEmployee(registration=mat)

                else:
                    print("Opcao invalida ou cancelada.")
                    pausar()
                    continue

                imprimir_resultados(resultados, ["ID", "Nome", "Matricula", "Foto"])

            except Exception as e:
                print(f"Erro na busca: {e}")
            pausar()

        elif opcao == '3':
            id_f = ler_int("ID do Funcionario a atualizar: ")
            if not id_f: continue

            nome = ler_input_opcional("Novo Nome: ")
            mat = ler_input_opcional("Nova Matricula: ")
            foto = ler_input_opcional("Caminho da Nova Foto: ")
            try:
                bd.updtEmployee(funcID=id_f, newname=nome, newregistration=mat,newphotopath=foto)
                print("Sucesso: Atualizado!")
            except Exception as e:
                print(f"Erro: {e}")
            pausar()

        elif opcao == '4':
            id_f = ler_int("ID do Funcionario a deletar: ")
            try:
                bd.deleteEmployee(funcID=id_f)
                print("Sucesso: Removido!")
            except Exception as e:
                print(f"Erro: {e}")
            pausar()

        elif opcao == '0':
            break


def menu_auxiliar(bd):
    while True:
        print("TABELAS AUXILIARES")
        print("1. Gestao de Cargos")
        print("2. Tipos de Manutencao")
        print("3. Tipos de Equipamento")
        print("0. Voltar")

        opcao = input("\nEscolha: ")

        if opcao == '1':
            print("\n--- Cargos ---")
            print("1. Criar")
            print("2. Buscar")
            print("3. Atualizar")
            print("4. Deletar")
            acao = input("Escolha: ").strip()

            try:
                if acao == '1':
                    bd.createCargo(input("Nome: "), ler_input_opcional("Descricao: "))
                    print("Sucesso: Cargo criado!")
                    pausar()

                elif acao == '2':
                    tipo, valor = pedir_criterio_busca("Cargo")
                    if tipo == 'id' and valor:
                        imprimir_resultados(bd.readCargo(cargoID=valor), ["ID", "Nome", "Descricao"])
                        pausar()
                    elif tipo == 'nome' and valor:
                        imprimir_resultados(bd.readCargo(name=valor), ["ID", "Nome", "Descricao"])
                        pausar()

                elif acao == '3':
                    bd.updtCargo(ler_int("ID para atualizar: "), ler_input_opcional("Novo Nome: "),
                                 ler_input_opcional("Nova Desc: "))
                    print("Sucesso: Cargo atualizado!")
                    pausar()

                elif acao == '4':
                    bd.deleteCargo(ler_int("ID para deletar: "))
                    print("Sucesso: Cargo deletado!")
                    pausar()
                else:
                    print("Opcao invalida.")
                    pausar()
            except Exception as e:
                print(f"Erro: {e}")
                pausar()

        elif opcao == '2':
            print("\n--- Tipos de Manutencao ---")
            print("1. Criar")
            print("2. Buscar")
            print("3. Atualizar")
            print("4. Deletar")
            acao = input("Escolha: ").strip()

            try:
                if acao == '1':
                    bd.createMaintType(input("Nome: "))
                    print("Sucesso: Tipo criado!")
                    pausar()

                elif acao == '2':
                    tipo, valor = pedir_criterio_busca("Tipo Manutencao")
                    if tipo == 'id' and valor:
                        imprimir_resultados(bd.readMaintType(typeID=valor), ["ID", "Nome"])
                        pausar()
                    elif tipo == 'nome' and valor:
                        imprimir_resultados(bd.readMaintType(name=valor), ["ID", "Nome"])
                        pausar()

                elif acao == '3':
                    bd.updtMaintType(ler_int("ID para atualizar: "), input("Novo Nome: "))
                    print("Sucesso: Atualizado!")
                    pausar()

                elif acao == '4':
                    bd.deleteMaintType(ler_int("ID para deletar: "))
                    print("Sucesso: Deletado!")
                    pausar()
                else:
                    print("Opcao invalida.")
                    pausar()
            except Exception as e:
                print(f"Erro: {e}")
                pausar()

        elif opcao == '3':
            print("\n--- Tipos de Equipamento ---")
            print("1. Criar")
            print("2. Buscar")
            print("3. Atualizar")
            print("4. Deletar")
            acao = input("Escolha: ").strip()

            try:
                if acao == '1':
                    nome = input("Nome: ")
                    reserva = input("Permite Reserva (S/N)? ").upper() == 'S'
                    bd.createEquipType(nome, reserva)
                    print("Sucesso: Tipo criado!")
                    pausar()

                elif acao == '2':
                    tipo, valor = pedir_criterio_busca("Tipo Equipamento")
                    if tipo == 'id' and valor:
                        imprimir_resultados(bd.readEquipType(typeID=valor), ["ID", "Nome", "Reserva?"])
                        pausar()
                    elif tipo == 'nome' and valor:
                        imprimir_resultados(bd.readEquipType(name=valor), ["ID", "Nome", "Reserva?"])
                        pausar()

                elif acao == '3':
                    nome = ler_input_opcional("Novo Nome: ")
                    res_in = ler_input_opcional("Permite Reserva (S/N ou enter): ")
                    reserva = (res_in.upper() == 'S') if res_in else None
                    bd.updtEquipType(ler_int("ID para atualizar: "), newname=nome, newallowreservation=reserva)
                    print("Sucesso: Atualizado!")
                    pausar()

                elif acao == '4':
                    bd.deleteEquipType(ler_int("ID para deletar: "))
                    print("Sucesso: Deletado!")
                    pausar()
                else:
                    print("Opcao invalida.")
                    pausar()
            except Exception as e:
                print(f"Erro: {e}")
                pausar()

        elif opcao == '0':
            break


def menu_view_agenda_reservas(bd):
    while True:
        print("CONSULTA DA VIEW: Agenda de Reservas")
        print("1. Listar todas as reservas")
        print("0. Voltar")
        opcao = input("\nEscolha: ")
        if opcao == '1':
            try:
                bd.db.cursor.execute("SELECT * FROM vw_agenda_reservas")
                resultados = bd.db.cursor.fetchall()
                imprimir_resultados(resultados, ["ID Reserva", "Usuario", "Equipamento", "Parque", "Inicio", "Fim", "Status"])
            except Exception as e:
                print(f"Erro: {e}")
            pausar()
        elif opcao == '0':
            break
        else:
            print("Opcao invalida.")
            pausar()


def menu_procedure_reserva(bd):
    while True:
        print("EXECUTAR PROCEDURE: Nova Reserva")
        print("1. Criar nova reserva (sp_nova_reserva)")
        print("0. Voltar")
        opcao = input("\nEscolha: ")
        if opcao == '1':
            try:
                id_usuario = ler_int("ID do Usuario: ")
                id_equipamento = ler_int("ID do Equipamento: ")
                inicio = input("Inicio (YYYY-MM-DD HH:MM:SS): ")
                fim = input("Fim (YYYY-MM-DD HH:MM:SS): ")
                bd.reservar_procedure(id_usuario, id_equipamento, inicio, fim)
                print("Reserva criada via procedure!")
            except Exception as e:
                print(f"Erro: {e}")
            pausar()
        elif opcao == '0':
            break
        else:
            print("Opcao invalida.")
            pausar()


def main():

    bd = ParqueBD()

    while True:
        print("SISTEMA DE GESTAO DE PARQUES")
        print("1. Gerenciar Parques")
        print("2. Gerenciar Usuarios")
        print("3. Gerenciar Funcionarios")
        print("4. Mais opções")
        print("5. Consultar Agenda de Reservas (VIEW)")
        print("6. Executar Procedure de Reserva")
        print("0. Sair")

        opcao = input("\nDigite sua opcao: ")

        if opcao == '1':
            menu_parque(bd)
        elif opcao == '2':
            menu_usuario(bd)
        elif opcao == '3':
            menu_funcionario(bd)
        elif opcao == '4':
            menu_auxiliar(bd)
        elif opcao == '5':
            menu_view_agenda_reservas(bd)
        elif opcao == '6':
            menu_procedure_reserva(bd)
        elif opcao == '0':
            print("\nEncerrando programa...")
            bd.quitDB()
            break
        else:
            print("Opcao invalida.")
            pausar()


if __name__ == "__main__":
    main()