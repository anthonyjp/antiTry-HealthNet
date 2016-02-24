from django.db import models

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female')
)

BLOOD_CHOICES = (
    ('A', 'A'),
    ('B', 'B'),
    ('AB', 'AB'),
    ('O', 'O')
)

INSURANCE_CHOICES = (
    ('Self Insured', 'Self Insured'),
    ('Blue Cross Blue Shield', 'Blue Cross Blue Shield'),
    ('Super Legit MI', 'Super Legit Medical Insurance'),
    ('Not Legit MI', 'Not Legit Medical Insurance')
)


class User(models.Model):
    firstName = models.CharField(max_length=100)
    middleInitial = models.CharField(max_length=1)
    lastName = models.CharField(max_length=100)
    email = models.EmailField()
    dateOfBirth = models.DateField()

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=GENDER_CHOICES[0][0])
    password = models.CharField(max_length=50)
    securityAnswer = models.CharField(max_length=50)


class Patient(User):
    height = models.PositiveIntegerField()
    weight = models.PositiveIntegerField()
    bloodType = models.CharField(max_length=2, choices=BLOOD_CHOICES, default=BLOOD_CHOICES[0][0])
    insurance = models.CharField(max_length=40, choices=INSURANCE_CHOICES, default=INSURANCE_CHOICES[0][0])
