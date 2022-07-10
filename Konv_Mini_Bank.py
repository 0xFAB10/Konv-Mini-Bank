def Format_Valor(valor:str)->str:
    ### Retorna a string valor padronizada.
    if ',' in str(valor):
        valor_format, centavos = valor.split(',')
    else:
        valor_format, centavos = str(valor), '00'
    valor_format = valor_format.replace('.', '')
    n = len(valor_format)//3 if len(valor_format)%3 else (len(valor_format)//3)-1
    for i in range(1,n+1):
        valor_format = f'{valor_format[:(-3*i)-(i-1)]}.{valor_format[(-3*i)-(i-1):]}'
    return f'R$ {valor_format},{centavos}'

def Read_Database_Notas()->str:
    ### Lê o banco de dados das cédulas.
    with open('notas_caixa.bin', mode='r')  as FILE:
        dct_notas = dict(i.replace('\n', '').split(' : ') for i in FILE.readlines())
    return dct_notas


def Write_Darabase_Notas(dct_notas:dict)->None:
    ### Grava as alterações no banco de dados das cédulas.
    try:
        with open('notas_caixa.bin', mode='w')  as FILE:
            FILE.writelines([f'{c[0]} : {c[1]}\n' for c in dct_notas.items()])
    except Exception as e:
        print('Database error', e)


def Check_Database_Clientes(cpf:str)->bool:
    ### Retorna a verificação se o CPF consta ou não no banco de dados.
    clientes = [c.replace('.bin', '') for c in listdir('clientes')]
    if cpf in clientes:
        return True
    return False


def Read_Database_Clientes(cpf:str)->list:
    ### Lê a base de dados e retorna o extrato do cliente.
    with open(join('clientes',cpf+'.bin'), mode='r') as FILE:
        extrato_cliente = [e.replace('\n', '').split(' : ') for e in FILE.readlines()]
    return extrato_cliente


def Write_Database_Clientes(cpf:str, info:str, valor:str, saldo:str)->None:
    ### Escreve uma linha na base de dados do cliente.
    data_hora = datetime.now().strftime('%d/%m/%Y %H:%M')
    try:
        with open(join('clientes',cpf+'.bin'), mode='a') as FILE:
            FILE.write(f'{data_hora} : {info} : {Format_Valor(valor)} : {Format_Valor(saldo)}\n')
    except Exception as e:
        print('Database error', e)


def Check_CPF(cpf_original:str)->(bool, str):
    ### Checa se o padrão do CPF e o digito verificador obedecem aos padrões aceitos.
    ### Retorna a verificação e o CPF padronizado.
    cpf = cpf_original.replace('.', ' ').replace('-', ' ')
    cpf = cpf.split(' ')
    # Checa se o CPF obedece o padrão xxx.xxx.xxx-xx ou padrão numérico.
    if '-'.join([str(len(c)) for c in cpf]) in ['3-3-3-2', '11']:
        cpf = ''.join(cpf)
        # Funções geradoras de código verificador
        V1 = lambda x : sum([int(d)*i for d,i in zip(x, range(10,1,-1))]) % 11
        V2 = lambda x : str(11 - x) if x > 1 else str(x)
        verificador_gerado = V2(V1(cpf[:9])) + V2(V1(cpf[1:10]))
        verificador_cpf = cpf[9:]
        if verificador_gerado == verificador_cpf:
            return True, cpf
    return False, cpf_original


def Criar_Cliente(cpf:str)->bool:
    ### Cria um novo arquivo para o CPF e retorna a verificação em caso de sucesso. 
    Write_Database_Clientes(cpf, 'Conta criada', '0', '0')
    return True


def Check_Valor(valor:str)->(bool,str):
    ### Verifica se o valor digitado é numérico, positivo e inteiro.
    ### Retorna a verificação e o valor padronizado.
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


def Check_Saque(valor:str)->(bool, str):
    ### Verifica se constam cédulas suficientes para o saque.
    ### Retorna verificação e mensagem.
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
            mensagem = f'Por favor, escolha um valor menor ou igual a {Format_Valor(soma)}.'
        else:
            minimo = min([int(i[0].replace('R$ ').replace(',00')) for i in dct_notas.items() if int(i[1]) > 0])
            mensagem = f'Por favor, escolha um valor múltiplo de {Format_Valor(minimo)} e menor ou igual a {Format_Valor(soma)}.'
        return False, f"Notas disponíveis insuficientes para o saque. {mensagem}"
    Write_Darabase_Notas(dct_notas)
    return True, f"Saque realizado na forma de {', '.join(str_retorno[:-1])} e {str_retorno[-1]}."


def Saldo(cpf:str)->str:
    ### Retorna o saldo do cliente
    saldo = Read_Database_Clientes(cpf)[-1][-1]
    return saldo


def Extrato_Saldo(cpf:str)->(list, str):
    ### Retorna o extrato e saldo padronizados.
    extrato_cliente = [f'{e[0]} {e[1]} {e[2]}' for e in Read_Database_Clientes(cpf)]
    saldo = Saldo(cpf)
    return extrato_cliente, saldo


def Deposito(cpf:str, valor:str)->(bool, str):
    ### Envia valor para checagem e envia informações para gravação no extrato.
    ### Retorna verificações e mensagem.
    check, valor = Check_Valor(valor)
    if check:
        saldo, centavos = Saldo(cpf).replace('R$ ','').replace('.', '').split(',')
        Write_Database_Clientes(cpf, 'DEPOSITO', valor, f'{int(saldo)+int(valor)},{centavos}')
        return True, f'Deposito de {Format_Valor(valor)} realizado com sucesso.'
    return False, f'{valor} não é um valor válido.'


def Saque(cpf:str, valor:str)->(bool, str):
    ### Envia valor para checagem, verifica se é menor que o saldo do cliente e envia informações para gravação no extrato.
    ### Retorna verificações e mensagem.
    mensagem = 'Valor inválido.'
    check, valor = Check_Valor(valor)
    if check:
        # Checa se o saldo é suficente
        mensagem = 'Saldo insuficiente.'
        saldo, centavos = Saldo(cpf).replace('R$ ','').replace('.', '').split(',')
        if int(valor) <= int(saldo):
            check, mensagem = Check_Saque(valor)
            if check:
                # Altera a base de dados
                Write_Database_Clientes(cpf, 'SAQUE', valor, f'{int(saldo)+int(valor)},{centavos}')
                return True, mensagem
    return False, mensagem

def Login(cpf:str)->(bool, str):
    ### Checa se o CPF é valido e cadastrado
    ### Retorna a verificação e o CPF padronizado
    check, cpf = Check_CPF(cpf)
    if check:
        if Check_Database_Clientes(cpf):
            print(f"\nBem vindo {cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}.")
            return True, cpf
        return Cadastro_CPF(cpf), cpf
    print('\nCPF inválido')
    return False, cpf

def Cadastro_CPF(cpf:str)->(bool):
    ### Cadastra novo usuário na base de dados
    ### Retorna verificação de sucesso.
    resposta = input('\nCPF não cadastrado. Deseja cadastrar-se? (s/n): ')
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


def Menu_Funcoes(opcao:str)->None:
    ### Recebe a opção selecionada pelo usuário, faz a limpeza e interpretação de dados e chama a função desejada.
    opcao = str(int(opcao)) if opcao.isnumeric() else opcao
    if opcao.lower().replace('ó', 'o') in ['1', 'hum', 'um', 'deposito', 'depositar']:
        check, cpf = Login(input('Informe o seu CPF: '))
        if check:
            check, mensagem = Deposito(cpf, input('Informe o valor que deseja depositar: '))
            print('\n'+mensagem)
    elif opcao.lower() in ['2', 'dois', 'saque', 'sacar']:
        check, cpf = Login(input('Informe o seu CPF: '))
        if check:
            print(f'\nSaldo atual: {Saldo(cpf)}')
            check, mensagem = Saque(cpf, input('Informe o valor que deseja sacar: '))
            print('\n'+mensagem)
    elif opcao.lower().replace(' ', '').replace('+', '') in ['3', 'tres', 'três', 'extratosaldo', 'extrato', 'saldo']:
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


def Menu_Principal()->None:
    ### Imprime o Menu e captura a opção escolhida pelo usuário.
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