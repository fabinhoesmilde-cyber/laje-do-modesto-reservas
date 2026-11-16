import re


def somente_digitos(texto):
    """Devolve só os números de um texto (ex.: '123.456' vira '123456')."""
    return re.sub(r"\D", "", str(texto or ""))


def cpf_valido(cpf):
    """Confere o tamanho e os dois dígitos verificadores do CPF."""
    digitos = somente_digitos(cpf)

    # Precisa ter 11 números e não pode ser repetido (111.111.111-11)
    if len(digitos) != 11 or digitos == digitos[0] * 11:
        return False

    for tamanho in (9, 10):
        soma = sum(
            int(digitos[i]) * (tamanho + 1 - i)
            for i in range(tamanho)
        )
        digito = (soma * 10 % 11) % 10

        if digito != int(digitos[tamanho]):
            return False

    return True


def formatar_cpf(cpf):
    """Devolve o CPF no formato 123.456.789-00, o mesmo que o site grava."""
    d = somente_digitos(cpf)
    return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"