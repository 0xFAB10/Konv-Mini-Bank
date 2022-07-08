def Read_Database_Notas():
    with open('notas_caixa.bin', mode='r')  as FILE:
        dct_notas = dict(i.replace('\n', '').split(' : ') for i in FILE.readlines())
    return dct_notas


def Write_Darabase_Notas(dct_notas):
    try:
        with open('notas_caixa.bin', mode='w')  as FILE:
            FILE.writelines([f'{c[0]} : {c[1]}\n' for c in dct_notas.items()])
    except Exception as e:
        print('Database error', e)


def Check_Database_Clientes(cpf):
    clientes = [c.replace('.bin', '') for c in listdir('clientes')]
    if cpf in clientes:
        return True
    return False


def Read_Database_Clientes(cpf):
    with open(join('clientes',cpf+'.bin'), mode='r') as FILE:
        extrato_cliente = [e.replace('\n', '').split(' : ') for e in FILE.readlines()]
    return extrato_cliente


def Write_Database_Clientes(cpf, info, valor, saldo):
    data_hora = datetime.now().strftime('%d/%m/%Y %H:%M')
    try:
        with open(join('clientes',cpf+'.bin'), mode='a') as FILE:
            FILE.write(f'{data_hora} : {info} : R$ {valor},00 : R$ {saldo},00\n')
    except Exception as e:
        print('Database error', e)


def Check_CPF(cpf):
    cpf = ''.join(c for c in cpf if c.isnumeric())
    cpf_padrao = f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'
    if len(cpf) == 11:
        # Funções geradoras de código verificador
        V1 = lambda x : sum([int(d)*i for d,i in zip(x, range(10,1,-1))]) % 11
        V2 = lambda x : str(11 - x) if x > 1 else str(x)
        verificador_gerado = V2(V1(cpf[:9])) + V2(V1(cpf[1:10]))
        _, verificador_cpf = cpf_padrao.split('-')
        if verificador_gerado == verificador_cpf:
            return True, cpf
    return False


def Criar_Cliente(cpf):
    Write_Database_Clientes(cpf, 'Conta criada', '0', '0')
    return True


def Check_Valor(valor):
    # verifica se o valor digitado é numérico, positivo e inteiro
    valor_teste = valor.replace('.',' ').replace(',', ' ')
    valor_teste = valor_teste.split(' ')
    if len(valor_teste) != 1:
        if len(valor_teste[-1]) == 2:
            if valor_teste[-1] != '00':
                return False, valor
            else:
                valor_teste = valor_teste[:-1]
        if len(valor_teste[-1]) == 1:
            if valor_teste[-1] != '0':
                return False, valor
            else:
                valor_teste = valor_teste[:-1]
        for v in valor_teste[1:-1]:
            if len(v) != 3:
                return False, valor
    valor_teste = ''.join(valor_teste)
    if valor_teste == '' or len([v for v in valor_teste if v.isnumeric()]) < len(valor_teste) or int(valor_teste) < 1:
        return False, valor
    return True, valor_teste


def Check_Saque(valor):
    dct_notas = Read_Database_Notas()
    resto = int(valor)
    # Calcula a quantidade de cada nota necessária para saque
    str_retorno = []
    for key in dct_notas:
        nota = int(key.replace('R$ ','').replace(',00', ''))
        quantidade_notas = 0
        if resto >= nota:
            quantidade_notas = resto//nota
            # Verifica se quantidade de notas é viável
            if quantidade_notas > int(dct_notas[key]):
                quantidade_notas = int(dct_notas[key])
            if quantidade_notas > 0:
                dct_notas[key] = str(int(dct_notas[key]) - quantidade_notas)
                resto -= quantidade_notas*nota
                s = '' if quantidade_notas == 1 else 's'
                str_retorno.append(f'{quantidade_notas} nota{s} de {key}')
    # Verifica se a quantidade de notas foi suficiente e gera mensagem de erro.
    if resto > 0:
        dct_notas = Read_Database_Notas()
        soma = sum([int(i[0].replace('R$ ','').replace(',00', ''))*int(i[1]) for i in dct_notas.items()])
        if soma == 0:
            mensagem = 'Caixa vazio no momento.'
        elif soma < int(valor):
            mensagem = f'Por favor, escolha um valor menor ou igual a R$ {soma},00.'
        else:
            minimo = min([i[0] for i in dct_notas.items() if int(i[1]) > 0])
            mensagem = f'Por favor, escolha um valor múltiplo de {minimo} e menor ou igual a R$ {soma},00.'
            if int(valor)-resto > 0:
                mensagem += f'Aconselhamos o saque de R$ {int(valor)-resto},00.'
        return False, f"Notas disponíveis insuficientes para o saque. {mensagem}"
    Write_Darabase_Notas(dct_notas)
    return True, f"Saque realizado na forma de {', '.join(str_retorno[:-1])} e {str_retorno[-1]}."


def Saldo(cpf):
    # Retorna o saldo do cliente
    saldo = Read_Database_Clientes(cpf)[-1][-1]
    return saldo


def Extrato_Saldo(cpf):
    # Retorna o extrato editado para exibição
    extrato_cliente = [f'{e[0]} {e[1]} {e[2]}' for e in Read_Database_Clientes(cpf)]
    saldo = Saldo(cpf)
    return extrato_cliente, saldo


def Deposito(cpf, valor):
    # Verifica o valor do deposito e faz a alteração na base de dados
    check, valor = Check_Valor(valor)
    if check:
        saldo = Saldo(cpf).replace('R$ ','').replace(',00', '')
        Write_Database_Clientes(cpf, 'DEPOSITO', valor, int(saldo)+int(valor))
        return True, f'Deposito de R$ {valor},00 realizado com sucesso.'
    return False, f'{valor} não é um valor válido.'


def Saque(cpf, valor):
    saldo = Saldo(cpf).replace('R$ ','').replace(',00', '')
    mensagem = 'Saldo insuficiente.'
    # Checa se o saldo é suficente
    if int(valor) < int(saldo):
        check, mensagem = Check_Saque(valor)
        if check:
            # Altera a base de dados
            Write_Database_Clientes(cpf, 'SAQUE', valor, int(saldo)-int(valor))
            return True, mensagem
    return False, mensagem

def Login(cpf):
    # Checa se o CPF é valido e cadastrado
    check, cpf = Check_CPF(cpf)
    if check:
        if Check_Database_Clientes(cpf):
            print(f"\nBem vindo {cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}.")
            return True, cpf
        return Cadastro_CPF(cpf), cpf
    print('\nCPF inválido')
    return False, cpf

def Cadastro_CPF(cpf):
    # Cadastra novo usuário na base de dados
    resposta = input('\nCPF não cadastrado. Deseja cadastrar-se? (s/n)')
    if resposta.lower() == 's'or resposta.lower() == 'sim':
        if Criar_Cliente(cpf):
            print('\nCPF cadastrado com sucesso.')
            return True
        else:
            print('\nErro ao cadastrar CPF.')
            return False
    elif resposta.lower() == 'n' or resposta.lower().replace('ã','a') == 'nao':
        return False
    else:
        print('\nDigite uma resposta válida.\nS ou SIM caso deseje se cadastrar.\nN ou NÃO caso não deseje se cadastrar.')
        return Cadastro_CPF(cpf)


def Menu_Funcoes(opcao):
    opcao = str(int(opcao)) if opcao.isnumeric() else opcao
    if opcao == '1' or opcao.lower().replace('h', '') == 'um':
        check, cpf = Login(input('Informe o seu CPF: '))
        if check:
            check, mensagem = Deposito(cpf, input('Informe o valor que deseja depositar:'))
            print('\n'+mensagem)
    elif opcao == '2' or opcao.lower() == 'dois':
        check, cpf = Login(input('Informe o seu CPF: '))
        if check:
            check, mensagem = Saque(cpf, input('Informe o valor que deseja sacar:'))
            print('\n'+mensagem)
    elif opcao == '3' or opcao.lower().replace('ê', 'e') == 'tres':
        check, cpf = Login(input('Informe o seu CPF: '))
        if check:
            mensagem, saldo = Extrato_Saldo(cpf)
            print()
            for m in mensagem:
                print(m)
            print('\n'+'Saldo atual:', saldo)
    else:
       print('\n'+'Opção Inválida.')
    input('\nTecle ENTER para continuar')


def Menu_Principal():
    print('\nBem vindo ao Konv Mini Bank!')
    print('Escolha uma das opções a seguir:\n')
    print('1 - Deposito')
    print('2 - Saque')
    print('3 - Extrato + Saldo')
    opcao = input('\nInforme o numero da opção escolhida: ')
    print()
    Menu_Funcoes(opcao)
    print()

from datetime import datetime
from os import listdir
from os.path import join

if __name__ == '__main__':
    while True:
        Menu_Principal()