from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncMonth

from .models import Profile, Complaint


# ======================
# HOME
# ======================
def home_view(request):
    return render(request, "home.html")


# ======================
# LOGIN
# ======================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            profile = get_object_or_404(Profile, user=user)
            role = profile.role.lower()

            if role == "admin":
                return redirect("admin_dashboard")
            elif role == "incharge":
                return redirect("incharge_dashboard")
            elif role == "student":
                return redirect("student_dashboard")
            elif role == "staff":
                return redirect("staff_dashboard")

        return render(request, "home.html", {
            "error": "Invalid username or password"
        })

    return redirect("home")


# ======================
# REGISTER
# ======================
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm = request.POST.get("password_confirm")
        role = request.POST.get("role")
        department = request.POST.get("department")

        if password != confirm:
            return render(request, "register.html", {
                "error": "Passwords do not match"
            })

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {
                "error": "Username already exists"
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        Profile.objects.create(
            user=user,
            role=role.lower(),
            department=department
        )

        return redirect("login")

    return render(request, "register.html")


# ======================
# PRIORITY DETECTION
# ======================
def detect_priority(description):
    description = description.lower()

    if any(word in description for word in ["urgent", "fire", "danger", "shock", "soon", "harassment",
                                            "immediate", "clean", "properly","academic", "emergency"]):
        return "High"

    if any(word in description for word in ["problem", "issue", "repair", "delay", "responsible", "maintainance",
                                            "not working", "not cleaning"]):
        return "Medium"

    return "Low"


# ======================
# STUDENT DASHBOARD
# ======================
@login_required
def student_dashboard(request):
    profile = Profile.objects.get(user=request.user)

    if profile.role.lower() != "student":
        return redirect("home")

    if request.method == "POST":
        description = request.POST.get("description")
        issue_department = request.POST.get("department")

        priority = detect_priority(description)

        Complaint.objects.create(
            department=issue_department,
            description=description,
            priority=priority,
            raised_by=request.user
        )

        return redirect("my_complaints")

    return render(request, "student_dashboard.html")


# ======================
# STAFF DASHBOARD
# ======================
@login_required
def staff_dashboard(request):
    profile = Profile.objects.get(user=request.user)

    if profile.role.lower() != "staff":
        return redirect("home")

    if request.method == "POST":
        description = request.POST.get("description")
        issue_department = request.POST.get("department")

        priority = detect_priority(description)

        Complaint.objects.create(
            department=issue_department,
            description=description,
            priority=priority,
            raised_by=request.user
        )

        return redirect("my_complaints")

    return render(request, "staff_dashboard.html")


# ======================
# MY COMPLAINTS
# ======================
@login_required
def my_complaints(request):
    complaints = Complaint.objects.filter(
        raised_by=request.user
    ).order_by("-created_at")

    return render(request, "my_complaints.html", {
        "complaints": complaints
    })


# ======================
# TRACK COMPLAINT
# ======================
@login_required
def track_complaint(request):
    complaint = None

    if request.method == "POST":
        ticket_id = request.POST.get("ticket_id")

        complaint = Complaint.objects.filter(
            ticket_id=ticket_id,
            raised_by=request.user
        ).first()

    return render(request, "track_complaint.html", {
        "complaint": complaint
    })


# ======================
# INCHARGE DASHBOARD
# ======================
@login_required
def incharge_dashboard(request):
    profile = Profile.objects.get(user=request.user)

    if profile.role.lower() != "incharge":
        return redirect("home")

    if request.method == "POST":
        complaint_id = request.POST.get("complaint_id")
        status = request.POST.get("status")

        complaint = Complaint.objects.get(id=complaint_id)
        complaint.status = status

        if status == "Resolved":
            complaint.resolved_at = timezone.now()

        complaint.save()
        return redirect("incharge_dashboard")

    # SHOW ALL COMPLAINTS (Single Incharge Control)
    complaints = Complaint.objects.all().order_by("-created_at")

    return render(request, "incharge_dashboard.html", {
        "complaints": complaints
    })


# ======================
# ADMIN DASHBOARD
# ======================
@login_required
def admin_dashboard(request):
    profile = Profile.objects.get(user=request.user)

    if profile.role.lower() != "admin":
        return redirect("home")

    total_complaints = Complaint.objects.count()

    status_counts = Complaint.objects.values("status").annotate(count=Count("status"))
    department_counts = Complaint.objects.values("department").annotate(count=Count("department"))
    priority_counts = Complaint.objects.values("priority").annotate(count=Count("priority"))

    monthly_counts = Complaint.objects.annotate(
        month=TruncMonth("created_at")
    ).values("month").annotate(count=Count("id")).order_by("month")

    context = {
        "total_complaints": total_complaints,
        "status_counts": status_counts,
        "department_counts": department_counts,
        "priority_counts": priority_counts,
        "monthly_counts": monthly_counts,
    }

    return render(request, "admin_dashboard.html", context)


# ======================
# FEEDBACK
# ======================
@login_required
def give_feedback(request, complaint_id):
    complaint = get_object_or_404(
        Complaint,
        id=complaint_id,
        raised_by=request.user
    )

    if complaint.status != "Resolved":
        return redirect("my_complaints")

    if request.method == "POST":
        feedback = request.POST.get("feedback")
        complaint.feedback = feedback
        complaint.save()
        return redirect("my_complaints")

    return render(request, "feedback.html", {
        "complaint": complaint
    })


# ======================
# LOGOUT
# ======================
def logout_view(request):
    logout(request)
    return redirect("home")