from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("discounts/", views.DiscountListView.as_view(), name="discount_list"),
    path("discounts/create/", views.DiscountCreateView.as_view(), name="discount_create"),
    path("discounts/<int:pk>/edit/", views.DiscountUpdateView.as_view(), name="discount_update"),
    path("discounts/<int:pk>/delete/", views.DiscountDeleteView.as_view(), name="discount_delete"),

    path("scholarships/", views.StudentScholarshipListView.as_view(), name="scholarship_list"),
    path("scholarships/request/", views.ScholarshipRequestView.as_view(), name="scholarship_request"),
    path("scholarships/<int:pk>/approve/", views.ScholarshipApproveView.as_view(), name="scholarship_approve"),

    path("", views.PaymentListView.as_view(), name="payment_list"),
    path("create/", views.PaymentCreateView.as_view(), name="payment_create"),
]
