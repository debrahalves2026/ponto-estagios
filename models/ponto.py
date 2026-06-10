class Ponto:
    def __init__(
        self,
        colaborador,
        data,
        entrada=None,
        saida_intervalo=None,
        retorno_intervalo=None,
        saida_final=None
    ):
        self.colaborador = colaborador
        self.data = data
        self.entrada = entrada
        self.saida_intervalo = saida_intervalo
        self.retorno_intervalo = retorno_intervalo
        self.saida_final = saida_final