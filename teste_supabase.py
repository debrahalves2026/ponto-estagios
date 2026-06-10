from supabase_client import supabase

dados = {
    "nome": "Teste Sistema",
    "vinculo": "Estagiário",
    "nucleo": "NPP",
    "turno": "Manhã",
    "horario": "08:00 às 12:00",
    "modalidade": "Presencial",
    "unidade_exercicio": "Teste",
    "procurador_monitor": "Teste",
    "celular": "11999999999",
    "login": "teste",
    "senha": "Novocolab123"
}

resultado = (
    supabase
    .table("colaboradores")
    .insert(dados)
    .execute()
)

print("Cadastro realizado!")
print(resultado)