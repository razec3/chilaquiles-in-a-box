from decimal import Decimal

from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from .domain import AperoPackageCalculator
from .exporters import JsonProcurementOrderExporter
from .forms import EventInputForm
from .repositories import MockRecipeRepository
from .services import PlanningSession, find_recipe_suggestions, purchase_limit

_recipe_repository = MockRecipeRepository()
_calculator = AperoPackageCalculator()


def health(request):
    return JsonResponse({"status": "ok"})


def event_input(request):
    if request.method == "POST":
        form = EventInputForm(request.POST)
        if form.is_valid():
            planning_session = PlanningSession(request)
            planning_session.start(
                guest_count=form.cleaned_data["guest_count"],
                maximum_budget=form.cleaned_data["budget"],
            )
            return redirect("event_in_a_box:suggestions")
    else:
        form = EventInputForm()

    return render(request, "event_in_a_box/event.html", {"form": form})


def suggestions(request):
    planning_session = PlanningSession(request)
    planning_request = planning_session.to_planning_request()
    if planning_request is None:
        return redirect("event_in_a_box:event_input")

    recipes = _recipe_repository.get_all()
    matches = find_recipe_suggestions(list(recipes), planning_request, _calculator)

    context = {
        "guest_count": planning_request.guest_count,
        "budget": planning_request.maximum_budget,
        "purchase_limit": purchase_limit(planning_request.maximum_budget),
        "suggestions": matches,
    }
    return render(request, "event_in_a_box/suggestions.html", context)


def select_recipe(request, recipe_id):
    if request.method != "POST":
        return redirect("event_in_a_box:suggestions")

    planning_session = PlanningSession(request)
    planning_request = planning_session.to_planning_request()
    if planning_request is None:
        return redirect("event_in_a_box:event_input")

    recipe = _recipe_repository.get_by_id(recipe_id)
    if recipe is None:
        raise Http404("Recipe not found.")

    eligible = find_recipe_suggestions([recipe], planning_request, _calculator)
    if not eligible:
        return redirect("event_in_a_box:suggestions")

    planning_session.select_recipe(recipe_id)
    return redirect("event_in_a_box:recipe_detail", recipe_id=recipe_id)


def recipe_detail(request, recipe_id):
    planning_session = PlanningSession(request)
    planning_request = planning_session.to_planning_request()
    if planning_request is None:
        return redirect("event_in_a_box:event_input")

    recipe = _recipe_repository.get_by_id(recipe_id)
    if recipe is None:
        raise Http404("Recipe not found.")

    package = _calculator.calculate([recipe], planning_request)

    context = {
        "recipe": recipe,
        "package": package,
        "guest_count": planning_request.guest_count,
    }
    return render(request, "event_in_a_box/recipe.html", context)


def confirm_recipe(request, recipe_id):
    if request.method != "POST":
        return redirect("event_in_a_box:recipe_detail", recipe_id=recipe_id)

    planning_session = PlanningSession(request)
    if planning_session.to_planning_request() is None:
        return redirect("event_in_a_box:event_input")

    if _recipe_repository.get_by_id(recipe_id) is None:
        raise Http404("Recipe not found.")

    planning_session.select_recipe(recipe_id)
    return redirect("event_in_a_box:order_review")


def order_review(request):
    planning_session = PlanningSession(request)
    planning_request = planning_session.to_planning_request()
    recipe_id = planning_session.selected_recipe_id
    if planning_request is None or recipe_id is None:
        return redirect("event_in_a_box:event_input")

    recipe = _recipe_repository.get_by_id(recipe_id)
    if recipe is None:
        raise Http404("Recipe not found.")

    package = _calculator.calculate([recipe], planning_request)
    limit = purchase_limit(planning_request.maximum_budget)
    remaining = limit - package.total_purchase_cost
    utilisation_percent = (
        round(package.total_purchase_cost / limit * 100) if limit > Decimal(0) else 0
    )

    context = {
        "recipe": recipe,
        "package": package,
        "guest_count": planning_request.guest_count,
        "budget": planning_request.maximum_budget,
        "purchase_limit": limit,
        "remaining": remaining,
        "utilisation_percent": utilisation_percent,
    }
    return render(request, "event_in_a_box/order.html", context)


def confirm_order(request):
    if request.method != "POST":
        return redirect("event_in_a_box:order_review")

    planning_session = PlanningSession(request)
    has_selection = planning_session.selected_recipe_id is not None
    if planning_session.to_planning_request() is None or not has_selection:
        return redirect("event_in_a_box:event_input")

    planning_session.confirm_order()
    return redirect("event_in_a_box:order_confirmation")


def order_confirmation(request):
    planning_session = PlanningSession(request)
    planning_request = planning_session.to_planning_request()
    recipe_id = planning_session.selected_recipe_id
    if planning_request is None or recipe_id is None or not planning_session.order_confirmed:
        return redirect("event_in_a_box:event_input")

    recipe = _recipe_repository.get_by_id(recipe_id)
    if recipe is None:
        raise Http404("Recipe not found.")

    package = _calculator.calculate([recipe], planning_request)
    limit = purchase_limit(planning_request.maximum_budget)
    remaining = limit - package.total_purchase_cost

    context = {
        "recipe": recipe,
        "package": package,
        "guest_count": planning_request.guest_count,
        "budget": planning_request.maximum_budget,
        "remaining": remaining,
    }
    return render(request, "event_in_a_box/confirmation.html", context)


def download_order(request):
    planning_session = PlanningSession(request)
    planning_request = planning_session.to_planning_request()
    recipe_id = planning_session.selected_recipe_id
    if planning_request is None or recipe_id is None or not planning_session.order_confirmed:
        return redirect("event_in_a_box:event_input")

    recipe = _recipe_repository.get_by_id(recipe_id)
    if recipe is None:
        raise Http404("Recipe not found.")

    package = _calculator.calculate([recipe], planning_request)
    document = JsonProcurementOrderExporter().export(package, planning_request.guest_count)

    response = HttpResponse(document.content, content_type=document.content_type)
    response["Content-Disposition"] = f'attachment; filename="{document.file_name}"'
    return response


def restart(request):
    PlanningSession(request).clear()
    return redirect("event_in_a_box:event_input")
