#crie uma funçao que recbe matrícula e email, e verifica se ambos são validos
# Dicionário com matrícula e email como valor (ajustado)
alunos = {
    2023304038: "nicoly@ifam.edu.br",
    2023315050: "carlos@ifam.edu.br"
}

def verificar_matricula_e_email(matricula, email):
    if matricula in alunos:
        if alunos[matricula] == email:
            print(f"A matrícula {matricula} pertence ao email {email}. Ambos são válidos.")
        else:
            print(f"A matrícula {matricula} é válida, mas o email não corresponde.")
    else:
        print(f"A matrícula {matricula} não é válida!")


    
    
verificar_matricula_e_email(2023304038, "nicoly@ifam.edu.br")
verificar_matricula_e_email(2023304038, "outro@email.com")
verificar_matricula_e_email(1111111111, "alguem@ifam.edu.br")