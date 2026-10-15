from django.db.models import Min, Q
from django.views.generic import ListView

from courses.models import Category, Course, CourseLevel, CourseModality, CourseStatus


class CourseSearchView(ListView):
    template_name = "search/course_search.html"
    context_object_name = "courses"
    paginate_by = 12

    def get_queryset(self):
        queryset = (
            Course.objects
            .filter(status=CourseStatus.PUBLISHED)
            .select_related("academy", "category")
        )

        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q)
                | Q(description__icontains=q)
                | Q(academy__name__icontains=q)
            )

        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category_id=category)

        level = self.request.GET.get("level")
        if level:
            queryset = queryset.filter(level=level)

        modality = self.request.GET.get("modality")
        if modality:
            queryset = queryset.filter(modality=modality)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_category = self.request.GET.get("category", "")
        current_level = self.request.GET.get("level", "")
        current_modality = self.request.GET.get("modality", "")

        context["categories"] = [
            {
                "pk": cat.pk,
                "name": cat.name,
                "selected": str(cat.pk) == current_category,
            }
            for cat in Category.objects.filter(is_active=True)
        ]

        context["levels"] = [
            {
                "value": value,
                "label": label,
                "selected": value == current_level,
            }
            for value, label in CourseLevel.choices
        ]

        context["modalities"] = [
            {
                "value": value,
                "label": label,
                "selected": value == current_modality,
            }
            for value, label in CourseModality.choices
        ]

        context["current_q"] = self.request.GET.get("q", "")
        context["current_category"] = current_category
        context["current_level"] = current_level
        context["current_modality"] = current_modality

        return context
