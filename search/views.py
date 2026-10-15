from django.db.models import Min, Q
from django.views.generic import ListView

from academies.models import Academy, Teacher
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


class GlobalSearchView(ListView):
    template_name = "search/global_search.html"
    context_object_name = "results"

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        if not q:
            return []

        results = []

        courses = (
            Course.objects
            .filter(status=CourseStatus.PUBLISHED)
            .filter(Q(title__icontains=q) | Q(description__icontains=q))
            .select_related("academy")
        )
        for course in courses[:20]:
            results.append({"type": "course", "obj": course})

        academies = (
            Academy.objects
            .filter(is_active=True)
            .filter(Q(name__icontains=q) | Q(description__icontains=q))
        )
        for academy in academies[:20]:
            results.append({"type": "academy", "obj": academy})

        teachers = (
            Teacher.objects
            .filter(is_active=True)
            .filter(
                Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(specialty__icontains=q)
            )
        )
        for teacher in teachers[:20]:
            results.append({"type": "teacher", "obj": teacher})

        return results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        return context
