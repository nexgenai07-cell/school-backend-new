from apps.common.models import BaseModel
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, role='student', **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    ROLE_CHOICES = [
        ('admin', 'Admin'), ('teacher', 'Teacher'),
        ('student', 'Student'), ('parent', 'Parent'), ('staff', 'Staff'),
    ]
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.name


class Student(BaseModel):
    GENDER_CHOICES = [('male', 'Male'), ('female', 'Female'), ('other', 'Other')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    class_obj = models.ForeignKey('academics.Class', on_delete=models.CASCADE, related_name='students')
    parent = models.ForeignKey('users.Parent', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    admission_no = models.CharField(max_length=50, unique=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    admission_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'students'

    def __str__(self):
        return f"{self.user.name} ({self.admission_no})"


class Teacher(BaseModel):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    employee = models.OneToOneField('hr.Employee', on_delete=models.CASCADE, related_name='teacher_profile')
    qualification = models.CharField(max_length=150, blank=True)
    experience = models.IntegerField(default=0, help_text="Years")
    join_date = models.DateField(null=True, blank=True)
    subject_specialization = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        db_table = 'teachers'

    def __str__(self):
        return self.user.name


class Staff(BaseModel):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    employee = models.OneToOneField('hr.Employee', on_delete=models.CASCADE, related_name='staff_profile')
    designation = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    join_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        db_table = 'staff'

    def __str__(self):
        return self.user.name


class Parent(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    occupation = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        db_table = 'parents'

    def __str__(self):
        return self.user.name
