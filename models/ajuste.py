class AjustePonto:
    def __init__(
        self,
        colaborador,
        data,
        tipo,
        horario,
        justificativa
    ):
        self.colaborador = colaborador
        self.data = data
        self.tipo = tipo
        self.horario = horario
        self.justificativa = justificativa
        self.status = "Pendente"