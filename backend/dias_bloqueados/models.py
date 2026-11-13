from django.db import models


class DiaBloqueado(models.Model):
    data = models.DateField(unique=True)

    motivo = models.CharField(
        max_length=255,
        blank=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        if self.motivo:
            return f"{self.data} - {self.motivo}"

        return str(self.data)