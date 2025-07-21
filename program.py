import textwrap
from abc import ABC, abstractmethod
from datetime import datetime

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
    
    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)
    
    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, cpf, nome, data_nascimento, endereco):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento
    
    def __str__(self):
        return f"{self.nome} (CPF: {self.cpf})"

class Historico:
    def __init__(self):
        self.transacoes = []
    
    def adicionar_transacao(self, transacao):
        self.transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now()
        })

class Conta:
    _contador_agencias = 1
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = f"{Conta._contador_agencias:04d}"
        Conta._contador_agencias += 1
        self._cliente = cliente
        self._historico = Historico()
    
    @classmethod
    def nova_conta(cls, numero, cliente):
        return cls(numero, cliente)
    @property
    def saldo(self):
        return self._saldo
    @property
    def numero(self):
        return self._numero
    @property
    def agencia(self):
        return self._agencia
    @property
    def cliente(self):
        return self._cliente
    @property
    def historico(self):
        return self._historico
    
    def sacar(self, valor):
        if valor > self._saldo:
            print("FALHA!! Saldo insuficiente.")
            return False
        elif valor <= 0:
            print("FALHA!! Valor inválido.")
            return False
        else:
            self._saldo -= valor
            print("Saque realizado!")
            return True
    
    def depositar(self, valor):
        if valor <= 0:
            print("FALHA!! Valor inválido")
            return False
        else:
            print("Deposito realizado!")
            self._saldo += valor
            return True
    
    def exibir_extrato(self):
        print("\n=== EXTRATO ===")
        if not self._historico.transacoes:
            print("Não foram realizadas movimentações.")
        else:
            for transacao in self._historico.transacoes:
                print(f"{transacao['tipo']}: R$ {transacao['valor']:.2f}")
        print(f"\nSaldo atual: R$ {self._saldo:.2f}")
    
    def __str__(self):
        return f"Agencia: {self.agencia} Conta: {self.numero} - Titular: {self.cliente.nome} - Saldo: R$ {self.saldo:.2f}"

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite = 500, limite_saques = 3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques
    
    def sacar(self, valor):
        numero_saques = 0
        hoje = datetime.now().date()

        for transacao in self.historico.transacoes:
            if (transacao["tipo"] == "Saque" and transacao["data"].date() == hoje):
                numero_saques += 1
        
        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_saques == True:
            print("FALHA!! O número de saques já se excedeu.")
            return False
        elif excedeu_limite == True:
            print("FALHA!! Valor acima do limite de saques.")
            return False
        else:
            return super().sacar(valor)

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass
    @abstractmethod
    def registrar(self, conta):
        pass

class Deposito(Transacao):
    def __init__(self, valor):
        self.valor = valor
    
    def registrar(self,conta):
        sucesso = conta.depositar(self.valor)
        if sucesso == True:
            conta.historico.adicionar_transacao(self)

class Saque(Transacao):
    def __init__(self, valor):
        self.valor = valor
    
    def registrar(self, conta):
        sucesso = conta.sacar(self.valor)
        if sucesso == True:
            conta.historico.adicionar_transacao(self)

def menu():
    menu = """\n
    +--------------------+
    |________MENU________|
    |[1]\tDepositar      |
    |[2]\tSacar          |
    |[3]\tExtrato        |
    |[4]\tNova conta     |
    |[5]\tListar contas  |
    |[6]\tNovo usuário   |
    |[0]\tSair           |
    +--------------------+
    => """
    return input(textwrap.dedent(menu))

def criar_usuario(lista_usuarios):
    cpf = input("Digite seu CPF: ")
    
    if buscar_usuario(cpf, lista_usuarios):
        print("FALHA!! Usuário já cadastrado.")
        return None
    
    nome = input("Digite seu nome: ")
    
    try:
        data_nascimento = datetime.strptime(input("Data de nascimento (dd/mm/aaaa): "), "%d/%m/%Y").date()
    except ValueError:
        print("Data inválida.")
        return None
    
    endereco = input("Digite seu endereço: ")
    return(cpf, nome, data_nascimento, endereco)

def buscar_usuario(cpf, lista_usuarios):
    for usuario in lista_usuarios:
        if usuario.cpf == cpf:
            return usuario
    return None

def buscar_conta(numero_conta, lista_contas):
    for conta in lista_contas:
        if conta.numero == numero_conta:
            return conta
    print("FALHA!! Conta não encontrada.")
    return None

def criar_conta(lista_usuarios, lista_contas):
    cpf = input("Digite seu CPF: ")
    usuario = buscar_usuario(cpf, lista_usuarios)

    if usuario:
        numero_conta = len(lista_contas)+ 1
        nova = ContaCorrente.nova_conta(numero_conta, usuario)
        lista_contas.append(nova)
        usuario.adicionar_conta(nova)
        print("Conta criada com sucesso!")
        return True
    else:
        print("FALHA!! faça o cadastro de usuário antes de continuar.")
        return None

def validar_saque(numero_conta):
        try:
            valor = float(input("Digite o valor que deseja sacar: "))
        except ValueError:
            print("FALHA!! entrada inválida")
            return None
        numero_conta.sacar(valor)

def validar_deposito(numero_conta):
        try:
            valor = float(input("Digite o valor que deseja depositar: "))
        except ValueError:
            print("FALHA!! entrada inválida")
            return None
        numero_conta.depositar(valor)

def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(conta)

def autenticar_conta(lista_contas):
    try:
        numero_conta = int(input("Digite o número da sua conta: "))
    except ValueError:
        print("FALHA!! Número da conta inválido.")
        return None
    
    conta = buscar_conta(numero_conta, lista_contas)
    if conta:
        cpf = input("Digite seu CPF: ")
        if conta.cliente.cpf != cpf:
            print("FALHA!! CPF não confere com o titular da conta.")
            return None
    return conta

def main():
    usuarios = []
    contas = []

    while(True):
        opcao = menu()
        if opcao == "1": #DEPOSITO
            conta = autenticar_conta(contas)
            if conta:
                validar_deposito(conta)
    
        elif opcao == "2": #SAQUE
            conta = autenticar_conta(contas)
            if conta:
                validar_saque(conta)
    
        elif opcao == "3": #EXTRATO
            conta = autenticar_conta(contas)
            if conta:
                conta.exibir_extrato()
    
        elif opcao == "4": #NOVA CONTA
            criar_conta(usuarios, contas)
    
        elif opcao == "5": #LISTAR CONTAS
            listar_contas(contas)
    
        elif opcao == "6": #NOVO USUÁRIO
            resultado = criar_usuario(usuarios)
            if resultado:
                cpf, nome, data_nascimento, endereco = resultado
                novo_usuario = PessoaFisica(cpf, nome, data_nascimento, endereco)
                usuarios.append(novo_usuario)
                print("Usuário criado com sucesso!")
        
        elif opcao == "0": #FIM DO PROGRAMA
            print("Obrigado por utilizar nossos serviços, até logo!")
            break

        else:
            print("FALHA!! Opção inválida.")
main()
