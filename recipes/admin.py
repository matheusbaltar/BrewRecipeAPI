from django.contrib import admin
from .models import (
    BeerStyle, Malt, Hop, Yeast,
    Recipe, RecipeMalt, RecipeHop, RecipeYeast,
    MashStep, FermentationStep, WaterProfile,
)


class RecipeMaltInline(admin.TabularInline):
    model = RecipeMalt
    extra = 1

class RecipeHopInline(admin.TabularInline):
    model = RecipeHop
    extra = 1

class RecipeYeastInline(admin.TabularInline):
    model = RecipeYeast
    extra = 1

class MashStepInline(admin.TabularInline):
    model = MashStep
    extra = 1
    ordering = ['order']

class FermentationStepInline(admin.TabularInline):
    model = FermentationStep
    extra = 1
    ordering = ['order']

class WaterProfileInline(admin.StackedInline):
    model = WaterProfile
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display  = ['name', 'style', 'author', 'batch_size_l', 'og', 'abv', 'ibu', 'ebc', 'created_at']
    list_filter   = ['style', 'created_at']
    search_fields = ['name', 'author', 'description']
    inlines       = [
        RecipeMaltInline, RecipeHopInline, RecipeYeastInline,
        MashStepInline, FermentationStepInline, WaterProfileInline,
    ]


@admin.register(BeerStyle)
class BeerStyleAdmin(admin.ModelAdmin):
    list_display  = ['bjcp_code', 'name']
    search_fields = ['name', 'bjcp_code']

@admin.register(Malt)
class MaltAdmin(admin.ModelAdmin):
    list_display  = ['name', 'malt_type', 'color_ebc', 'producer', 'origin_country']
    list_filter   = ['malt_type', 'origin_country']
    search_fields = ['name', 'producer']

@admin.register(Hop)
class HopAdmin(admin.ModelAdmin):
    list_display  = ['name', 'hop_type', 'form', 'alpha_acid_pct', 'origin_country']
    list_filter   = ['hop_type', 'form', 'origin_country']
    search_fields = ['name', 'aroma_profile']

@admin.register(Yeast)
class YeastAdmin(admin.ModelAdmin):
    list_display  = ['name', 'yeast_type', 'temp_min_c', 'temp_max_c']
    list_filter   = ['yeast_type']
    search_fields = ['name']
