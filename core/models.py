from django.db import models



class ContactMessage(models.Model):
    """
    Mensaje enviado desde el formulario de contacto.
    """

    name = models.CharField(
        max_length=150,
        verbose_name="Nombre",
    )

    email = models.EmailField(
        verbose_name="Email",
    )

    subject = models.CharField(
        max_length=200,
        verbose_name="Asunto",
    )

    message = models.TextField(
        verbose_name="Mensaje",
    )

    is_read = models.BooleanField(
        default=False,
        verbose_name="Leído",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de envío",
    )

    class Meta:
        verbose_name = "Mensaje de contacto"
        verbose_name_plural = "Mensajes de contacto"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_read"]),
        ]


    def __str__(self):
        return f"{self.subject} — {self.name}"

