from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("", views.CourseListView.as_view(), name="list"),
    path("create/", views.CourseCreateView.as_view(), name="create"),
    path("mine/", views.MyCourseListView.as_view(), name="mine"),

    # ---------------------------------------------------------------
    # Categorías
    # ---------------------------------------------------------------
    path(
        "categories/",
        views.CategoryListView.as_view(),
        name="category_list",
    ),
    path(
        "categories/create/",
        views.CategoryCreateView.as_view(),
        name="category_create",
    ),
    path(
        "categories/<slug:slug>/",
        views.CategoryDetailView.as_view(),
        name="category_detail",
    ),
    path(
        "categories/<slug:slug>/edit/",
        views.CategoryUpdateView.as_view(),
        name="category_update",
    ),
    path(
        "categories/<slug:slug>/delete/",
        views.CategoryDeleteView.as_view(),
        name="category_delete",
    ),

    # ---------------------------------------------------------------
    # Cursos — IMPORTANTE: las rutas específicas (edit/delete)
    # van ANTES de la genérica <pk>/<slug>/, porque <slug:slug>
    # captura cualquier cosa (incluido "edit" o "delete") y si va
    # primero se come a las demás.
    # ---------------------------------------------------------------
    path(
        "<int:pk>/edit/",
        views.CourseUpdateView.as_view(),
        name="update",
    ),
    path(
        "<int:pk>/delete/",
        views.CourseDeleteView.as_view(),
        name="delete",
    ),
    path(
        "<int:pk>/<slug:slug>/",
        views.CourseDetailView.as_view(),
        name="detail",
    ),

    # ---------------------------------------------------------------
    # Convocatorias
    # ---------------------------------------------------------------
    path(
        "<int:course_pk>/convocatorias/create/",
        views.ConvocatoriaCreateView.as_view(),
        name="convocatoria_create",
    ),
    path(
        "convocatorias/<int:pk>/edit/",
        views.ConvocatoriaUpdateView.as_view(),
        name="convocatoria_update",
    ),
    path(
        "convocatorias/<int:pk>/delete/",
        views.ConvocatoriaDeleteView.as_view(),
        name="convocatoria_delete",
    ),

    # ---------------------------------------------------------------
    # Imágenes de curso
    # ---------------------------------------------------------------
    path(
        "<int:course_pk>/images/create/",
        views.CourseImageCreateView.as_view(),
        name="course_image_create",
    ),
    path(
        "images/<int:pk>/edit/",
        views.CourseImageUpdateView.as_view(),
        name="course_image_update",
    ),
    path(
        "images/<int:pk>/delete/",
        views.CourseImageDeleteView.as_view(),
        name="course_image_delete",
    ),

    path(
    "favorites/",
    views.CourseFavoriteListView.as_view(),
    name="favorites",
    ),
    path(
        "<int:pk>/favorite/",
        views.toggle_course_favorite,
        name="toggle_favorite",
    ),  
]