from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import Secret


@require_http_methods(["GET", "POST"])
def secret_detail(request, pk):
    secret = get_object_or_404(Secret, pk=pk)

    if secret.is_expired() and request.method == "GET":
        raise Http404

    if request.method == "POST":
        with transaction.atomic():
            secret = Secret.objects.select_for_update().get(pk=pk)
            if secret.is_expired():
                raise Http404
            secret.viewed_at = timezone.now()
            secret.save(update_fields=["viewed_at"])
        return render(
            request,
            "secretshare/secret_detail.html",
            {"reveal": True, "content": secret.content},
        )

    return render(request, "secretshare/secret_detail.html", {})
