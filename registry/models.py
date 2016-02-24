from django.db import models

# Create your models here.
class Patient(models.Model):
    firstName = models.CharField(max_length=100)
    middleInitial = models.CharField(max_length=1)
    lastName = models.CharField(max_length=100)
    dateOfBirth = models.DateField()
    MALE = 'M'
    FEMALE = 'F'
    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female')
    )
    gender = models.CharField(max_length=1,
                                      choices=GENDER_CHOICES,
                                      default=MALE)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=50)
    securityAnswer = models.CharField(max_length=50)
    height = models.IntegerField()
    weight = models.IntegerField()
    OTYPE = 'O'
    ATYPE = 'A'
    BTYPE = 'B'
    ABTYPE = 'AB'
    BLOOD_CHOICES = (
        (OTYPE, 'O'),
        (ATYPE, 'A'),
        (BTYPE, 'B'),
        (ABTYPE, 'AB')
    )
    bloodType = models.CharField(max_length=2, choices = BLOOD_CHOICES,default = OTYPE)
    SELF = 'self'
    BCBS = 'bcbs'
    SLMI = 'slmi'
    NLMI = 'nlmi'
    INSURANCE_CHOICES = (
        (SELF, 'Self Insured'),
        (BCBS, 'Blue Cross Blue Shield'),
        (SLMI, 'Super Legit Medical Insurance'),
        (NLMI, 'Not Legit Medical Insurance')
    )
    insurance = models.CharField(max_length =4, choices = INSURANCE_CHOICES, default = SELF)

    def __str__(self):
        return self.lastName