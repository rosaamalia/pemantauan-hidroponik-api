from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from django.core.exceptions import PermissionDenied

def paginated_queryset(queryset, request, pagination_class=PageNumberPagination()):
    # Mengembalikan hasil queryset dalam bentuk paginated
    # PAGE_SIZE secara default mengikuti setting

    paginator = pagination_class
    paginator.page_size = settings.REST_FRAMEWORK["PAGE_SIZE"]
    result_page = paginator.paginate_queryset(queryset, request)
    return (paginator, result_page)

def verifikasi_id_akun(id_jwt, id_akun):
    # Memastikan seorang pengguna hanya mengakses data miliknya saja
    if id_jwt != id_akun:
        raise PermissionDenied()