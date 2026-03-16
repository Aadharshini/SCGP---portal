from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


# =========================
# PROFILE MODEL
# =========================
class Profile(models.Model):

    ROLE_CHOICES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('incharge', 'Grievance Incharge'),
        ('admin', 'Admin'),
    )

    DEPARTMENT_CHOICES = (
    ('ba_english_literature', 'B.A.English Literature'),  
    ('bcom', 'B.Com'),
    ('bcom_ca', 'B.Com (Computer Applications)'),
    ('bcom_pa', 'B.Com (Professional Accounting)'),
    ('bsc_cs', 'B.Sc Computer Science'),
    ('bsc_cs_da', 'B.Sc CS with Data Analytics'),
    ('bsc_it', 'B.Sc Information Technology'),
    ('bca', 'BCA (Comp. Applications)'),
    ('cdf', 'Costume Design & Fashion (CDF)'),
    ('bba_ca', 'BBA CA'),
    ('bsc_maths', 'B.Sc Mathematics'),
    ('bsc_chem', 'B.Sc Chemistry'),
    ('bsc_phy', 'B.Sc Physics'),
    ('bsc_botany', 'B.Sc Botany'),
    ('bsc_zoology', 'B.Sc Zoology'),
    ('mcom', 'M.Com'),
    ('msc_chemistry', 'M.Sc Chemistry'),
    ('msc_physics', 'M.Sc Physics'),
    ('mcom_ca', 'M.Com CA'),
)
       

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)

    def __str__(self):
        return self.user.username


# =========================
# COMPLAINT MODEL
# =========================
class Complaint(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]

    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]

    # Issue department (Hostel, Library etc.)
    ISSUE_DEPARTMENT_CHOICES = [
        ('Hostel', 'Hostel'),
        ('Library', 'Library'),
        ('Transport', 'Transport'),
        ('Academic', 'Academic'),
        ('Canteen', 'Canteen'),
        ('Infrastructure', 'Infrastructure'),
        ('Stationary', 'Stationary'),
        ('Administration', 'Administration'),
        ('Security', 'Security'),
        ('FirstAid/Medical', 'FirstAid/Medical'),
        ('Events/Extracurricular', 'Events/Extracurricular'),
    ]

    ticket_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    department = models.CharField(
        max_length=100,
        choices=ISSUE_DEPARTMENT_CHOICES
    )

    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='Low'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    raised_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='complaints'
    )

    # Feedback from student after resolution
    feedback = models.TextField(null=True, blank=True)

    # =========================
    # AUTO LOGIC
    # =========================
    def save(self, *args, **kwargs):

        # Generate ticket ID
        if not self.ticket_id:
            self.ticket_id = "SCGP" + str(uuid.uuid4().int)[:6]

        # Auto-set resolved time
        if self.status == "Resolved" and not self.resolved_at:
            self.resolved_at = timezone.now()

        super().save(*args, **kwargs)

    # Show newest complaints first
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.ticket_id