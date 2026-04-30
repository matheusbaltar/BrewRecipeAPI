from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    BeerStyle, Malt, Hop, Yeast,
    Recipe, RecipeMalt, RecipeHop, RecipeYeast,
    MashStep, FermentationStep,
)
from .serializers import (
    BeerStyleSerializer,
    MaltSerializer,
    HopSerializer,
    YeastSerializer,
    RecipeListSerializer,
    RecipeDetailSerializer,
    RecipeWriteSerializer,
    RecipeMaltSerializer,
    RecipeHopSerializer,
    RecipeYeastSerializer,
    MashStepSerializer,
    FermentationStepSerializer,
)


# ─────────────────────────────────────────────
#  Viewsets por Categorias (Lupulos, Maltes)
# ─────────────────────────────────────────────

class BeerStyleViewSet(viewsets.ModelViewSet):
    queryset = BeerStyle.objects.all()
    serializer_class = BeerStyleSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'bjcp_code']
    ordering_fields = ['name', 'bjcp_code']


class MaltViewSet(viewsets.ModelViewSet):
    queryset = Malt.objects.all()
    serializer_class = MaltSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['malt_type', 'origin_country']
    search_fields = ['name', 'producer']
    ordering_fields = ['name', 'color_ebc']


class HopViewSet(viewsets.ModelViewSet):
    queryset = Hop.objects.all()
    serializer_class = HopSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['hop_type', 'form', 'origin_country']
    search_fields = ['name', 'aroma_profile']
    ordering_fields = ['name', 'alpha_acid_pct']


class YeastViewSet(viewsets.ModelViewSet):
    queryset = Yeast.objects.all()
    serializer_class = YeastSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['yeast_type', 'flocculation', 'lab']
    search_fields = ['name', 'code', 'lab']
    ordering_fields = ['name', 'attenuation_min_pct']


# ─────────────────────────────────────────────
# Viewsets de Receita
# ─────────────────────────────────────────────

class RecipeViewSet(viewsets.ModelViewSet):
    """
    list:   GET  /api/recipes/           – listas (lightweight)
    create: POST /api/recipes/           – criar com ingredientes aninhados
    retrieve: GET /api/recipes/{id}/     – todos os detalhes dos dados
    update: PUT  /api/recipes/{id}/      – update completos dos itens aninhados
    partial_update: PATCH /api/recipes/{id}/
    destroy: DELETE /api/recipes/{id}/
    """
    queryset = Recipe.objects.select_related('style').prefetch_related(
        'malts__malt', 'hops__hop', 'yeasts__yeast',
        'mash_steps', 'fermentation_steps', 'water_profile',
    ).all()

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['style', 'author']
    search_fields = ['name', 'description', 'author', 'style__name']
    ordering_fields = ['name', 'created_at', 'og', 'abv', 'ibu', 'ebc']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeDetailSerializer


# ─────────────────────────────────────────────
#  Viewsets de ingredientes aninhados (limitado por receita)
# ─────────────────────────────────────────────

class RecipeMaltViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeMaltSerializer

    def get_queryset(self):
        return RecipeMalt.objects.filter(recipe_id=self.kwargs['recipe_pk'])

    def perform_create(self, serializer):
        serializer.save(recipe_id=self.kwargs['recipe_pk'])


class RecipeHopViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeHopSerializer

    def get_queryset(self):
        return RecipeHop.objects.filter(recipe_id=self.kwargs['recipe_pk'])

    def perform_create(self, serializer):
        serializer.save(recipe_id=self.kwargs['recipe_pk'])


class RecipeYeastViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeYeastSerializer

    def get_queryset(self):
        return RecipeYeast.objects.filter(recipe_id=self.kwargs['recipe_pk'])

    def perform_create(self, serializer):
        serializer.save(recipe_id=self.kwargs['recipe_pk'])


class MashStepViewSet(viewsets.ModelViewSet):
    serializer_class = MashStepSerializer

    def get_queryset(self):
        return MashStep.objects.filter(recipe_id=self.kwargs['recipe_pk'])

    def perform_create(self, serializer):
        serializer.save(recipe_id=self.kwargs['recipe_pk'])


class FermentationStepViewSet(viewsets.ModelViewSet):
    serializer_class = FermentationStepSerializer

    def get_queryset(self):
        return FermentationStep.objects.filter(recipe_id=self.kwargs['recipe_pk'])

    def perform_create(self, serializer):
        serializer.save(recipe_id=self.kwargs['recipe_pk'])
