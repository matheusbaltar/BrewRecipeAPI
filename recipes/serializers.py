from rest_framework import serializers
from .models import (
    BeerStyle, Malt, Hop, Yeast,
    Recipe, RecipeMalt, RecipeHop, RecipeYeast,
    MashStep, FermentationStep, WaterProfile,
)


class BeerStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeerStyle
        fields = '__all__'


class MaltSerializer(serializers.ModelSerializer):
    class Meta:
        model = Malt
        fields = '__all__'


class HopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hop
        fields = '__all__'


class YeastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Yeast
        fields = '__all__'



class RecipeMaltSerializer(serializers.ModelSerializer):
    malt_detail = MaltSerializer(source='malt', read_only=True)

    class Meta:
        model = RecipeMalt
        fields = ['id', 'malt', 'malt_detail', 'amount_kg', 'percentage']


class RecipeHopSerializer(serializers.ModelSerializer):
    hop_detail = HopSerializer(source='hop', read_only=True)

    class Meta:
        model = RecipeHop
        fields = ['id', 'hop', 'hop_detail', 'amount_g', 'use', 'time_min', 'ibu_contribution']


class RecipeYeastSerializer(serializers.ModelSerializer):
    yeast_detail = YeastSerializer(source='yeast', read_only=True)

    class Meta:
        model = RecipeYeast
        fields = ['id', 'yeast', 'yeast_detail', 'amount', 'starter', 'starter_size_l']


class MashStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = MashStep
        fields = ['id', 'name', 'step_type', 'temp_c', 'time_min',
                  'water_l', 'water_temp_c', 'order']


class FermentationStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = FermentationStep
        fields = ['id', 'stage', 'temp_c', 'duration_days', 'notes', 'order']


class WaterProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterProfile
        fields = ['id', 'calcium_ppm', 'magnesium_ppm', 'sodium_ppm',
                  'chloride_ppm', 'sulfate_ppm', 'bicarbonate_ppm', 'ph']


#  serializers das receitas


class RecipeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    style_name = serializers.CharField(source='style.name', read_only=True, default=None)

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'style', 'style_name', 'author',
            'batch_size_l', 'og', 'fg', 'abv', 'ibu', 'ebc',
            'created_at',
        ]


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Full serializer with all nested data – used for retrieve/create/update."""
    style_detail        = BeerStyleSerializer(source='style', read_only=True)
    malts               = RecipeMaltSerializer(many=True, read_only=True)
    hops                = RecipeHopSerializer(many=True, read_only=True)
    yeasts              = RecipeYeastSerializer(many=True, read_only=True)
    mash_steps          = MashStepSerializer(many=True, read_only=True)
    fermentation_steps  = FermentationStepSerializer(many=True, read_only=True)
    water_profile       = WaterProfileSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'style', 'style_detail', 'description', 'author',
            'batch_size_l', 'boil_volume_l', 'boil_time_min', 'efficiency_pct',
            'og', 'fg', 'abv', 'ibu', 'ebc', 'srm',
            'notes', 'created_at', 'updated_at',
            'malts', 'hops', 'yeasts',
            'mash_steps', 'fermentation_steps', 'water_profile',
        ]


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Writable serializer that accepts nested ingredient lists on create/update."""
    malts               = RecipeMaltSerializer(many=True, required=False)
    hops                = RecipeHopSerializer(many=True, required=False)
    yeasts              = RecipeYeastSerializer(many=True, required=False)
    mash_steps          = MashStepSerializer(many=True, required=False)
    fermentation_steps  = FermentationStepSerializer(many=True, required=False)
    water_profile       = WaterProfileSerializer(required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'style', 'description', 'author',
            'batch_size_l', 'boil_volume_l', 'boil_time_min', 'efficiency_pct',
            'og', 'fg', 'abv', 'ibu', 'ebc', 'srm', 'notes',
            'malts', 'hops', 'yeasts',
            'mash_steps', 'fermentation_steps', 'water_profile',
        ]

    def _save_nested(self, recipe, malts, hops, yeasts, mash_steps, fermentation_steps, water_profile):
        for m in malts:
            RecipeMalt.objects.create(recipe=recipe, **m)
        for h in hops:
            RecipeHop.objects.create(recipe=recipe, **h)
        for y in yeasts:
            RecipeYeast.objects.create(recipe=recipe, **y)
        for step in mash_steps:
            MashStep.objects.create(recipe=recipe, **step)
        for step in fermentation_steps:
            FermentationStep.objects.create(recipe=recipe, **step)
        if water_profile:
            WaterProfile.objects.create(recipe=recipe, **water_profile)

    def create(self, validated_data):
        malts               = validated_data.pop('malts', [])
        hops                = validated_data.pop('hops', [])
        yeasts              = validated_data.pop('yeasts', [])
        mash_steps          = validated_data.pop('mash_steps', [])
        fermentation_steps  = validated_data.pop('fermentation_steps', [])
        water_profile       = validated_data.pop('water_profile', None)

        recipe = Recipe.objects.create(**validated_data)
        self._save_nested(recipe, malts, hops, yeasts, mash_steps, fermentation_steps, water_profile)
        return recipe

    def update(self, instance, validated_data):
        malts               = validated_data.pop('malts', None)
        hops                = validated_data.pop('hops', None)
        yeasts              = validated_data.pop('yeasts', None)
        mash_steps          = validated_data.pop('mash_steps', None)
        fermentation_steps  = validated_data.pop('fermentation_steps', None)
        water_profile       = validated_data.pop('water_profile', None)


        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()



        if malts is not None:
            instance.malts.all().delete()
            for m in malts:
                RecipeMalt.objects.create(recipe=instance, **m)

        if hops is not None:
            instance.hops.all().delete()
            for h in hops:
                RecipeHop.objects.create(recipe=instance, **h)

        if yeasts is not None:
            instance.yeasts.all().delete()
            for y in yeasts:
                RecipeYeast.objects.create(recipe=instance, **y)

        if mash_steps is not None:
            instance.mash_steps.all().delete()
            for step in mash_steps:
                MashStep.objects.create(recipe=instance, **step)

        if fermentation_steps is not None:
            instance.fermentation_steps.all().delete()
            for step in fermentation_steps:
                FermentationStep.objects.create(recipe=instance, **step)

        if water_profile is not None:
            WaterProfile.objects.filter(recipe=instance).delete()
            WaterProfile.objects.create(recipe=instance, **water_profile)

        return instance
