from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)


class Type(models.Model):
    name = models.CharField(max_length=200, unique=True)


class Publisher(models.Model):
    name = models.CharField(max_length=200, unique=True)


class CompetitionNotice(models.Model):
    code = models.CharField(max_length=64, primary_key=True)
    header = models.CharField(max_length=2048)
    url = models.CharField(max_length=512)
    pub_date = models.DateField()
    comp_date = models.DateField(null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    comp_type = models.ForeignKey(Type, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
