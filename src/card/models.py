from django.db import models
import uuid

class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)

class Card(models.Model):
    unique_id = models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4)
    status = models.CharField(max_length=20, blank=False, default="begin interviewing")
    job_title = models.CharField(max_length=255, blank=False)
    associated_company = models.ForeignKey(Company)

    def __str__(self):
        return "A card for " + self.associated_company.name

class Tag(models.Model):
    tag = models.CharField(max_length=100)
    tagged_card = models.ForeignKey(Card)

    def __str__(self):
        return self.tag

class Contact(models.Model):
    name = models.CharField(max_length=255, blank=False)
    phone = models.CharField(max_length=255, blank=False)
    email = models.EmailField()
    associated_card = models.ForeignKey(Card)

    def __str__(self):
        return "Contact with name " + self.name

