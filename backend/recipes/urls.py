from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers

from .views import (
    BeerStyleViewSet,
    MaltViewSet,
    HopViewSet,
    YeastViewSet,
    RecipeViewSet,
    RecipeMaltViewSet,
    RecipeHopViewSet,
    RecipeYeastViewSet,
    MashStepViewSet,
    FermentationStepViewSet,
)

# ──rotas principais
router = DefaultRouter()
router.register(r'styles',  BeerStyleViewSet, basename='style')
router.register(r'malts',   MaltViewSet,      basename='malt')
router.register(r'hops',    HopViewSet,       basename='hop')
router.register(r'yeasts',  YeastViewSet,     basename='yeast')
router.register(r'recipes', RecipeViewSet,    basename='recipe')

# ──/api/recipes/{recipe_pk}/...
recipes_router = nested_routers.NestedDefaultRouter(router, r'recipes', lookup='recipe')
recipes_router.register(r'malts',              RecipeMaltViewSet,       basename='recipe-malt')
recipes_router.register(r'hops',               RecipeHopViewSet,        basename='recipe-hop')
recipes_router.register(r'yeasts',             RecipeYeastViewSet,      basename='recipe-yeast')
recipes_router.register(r'mash-steps',         MashStepViewSet,         basename='recipe-mash-step')
recipes_router.register(r'fermentation-steps', FermentationStepViewSet, basename='recipe-fermentation-step')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(recipes_router.urls)),
]
