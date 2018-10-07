from django.db import models

class BaseSrer(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        db_tablespace = 'srer'


class Raingage(BaseSrer):

    code = models.CharField(null=True, blank=True, max_length=125)

    name = models.CharField(null=True, blank=True, max_length=125)

    latitude = models.DecimalField(null=True, blank=True, max_digits=15, decimal_places=5)

    longitude = models.DecimalField(null=True, blank=True, max_digits=15, decimal_places=5)

    class Meta:
        verbose_name = 'Raingage'
        verbose_name_plural = 'Raingages'

    def __repr__(self):
        return u'{}'.format(self.id)

    def __str__(self):
        return u'{}'.format(self.name)

    def str(self):
        return self.name

class PrecipEvent(BaseSrer):

    year = models.IntegerField(blank=True, null=True)

    month = models.IntegerField(blank=True, null=True)

    precip = models.DecimalField(blank=True, null=True, max_digits=50, decimal_places=10)

    raingage = models.ForeignKey(Raingage, on_delete=models.CASCADE, db_index=True)

    class Meta:
        verbose_name = 'Precip Events'
        verbose_name_plural = 'Precip Events'
