class Colaborador:
    def __init__(
        self,
        nome,
        vinculo,
        nucleo,
        turno,
        horario,
        modalidade,
        unidade_exercicio,
        procurador_monitor,
        celular,
        login,
        senha="Novocolab123"
    ):
        self.nome = nome
        self.vinculo = vinculo
        self.nucleo = nucleo
        self.turno = turno
        self.horario = horario
        self.modalidade = modalidade
        self.unidade_exercicio = unidade_exercicio
        self.procurador_monitor = procurador_monitor
        self.celular = celular
        self.login = login
        self.senha = senha
        self.primeiro_acesso = True
        self.ativo = True