from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator



#   Cadastro de Ingredientes
# ─────────────────────────────────────────────

class BeerStyle(models.Model):
    """Estilo de cerveja BJCP (ex: "American IPA", "Munich Helles")."""
    name        = models.CharField(max_length=100, unique=True)
    bjcp_code   = models.CharField(max_length=10, blank=True, help_text="ex: 21A")
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.bjcp_code} – {self.name}" if self.bjcp_code else self.name

    class Meta:
        ordering = ['name']


#   Maltes
#─────────────────────────────────────────────

class Malt(models.Model):
    """Malte fermentável: maltes base, cristal/caramelo, torrados, adjuntos."""
    TYPE_CHOICES = [
        ('base',      'Malte Base'),
        ('caramel',   'Caramel / Cristal'),
        ('roasted',   'Torrado'),
        ('adjunct',   'Adjunto / Açúcar'),
        ('other',     'Outro'),
    ]

    name            = models.CharField(max_length=150)
    producer        = models.CharField(max_length=100, blank=True)
    origin_country  = models.CharField(max_length=100, blank=True)
    malt_type       = models.CharField(max_length=20, choices=TYPE_CHOICES, default='base')
    color_ebc       = models.FloatField(help_text="Cor em unidades EBC",
                                        validators=[MinValueValidator(0)])
    potential_sg    = models.FloatField(null=True, blank=True,
                                        help_text="Potencial máximo de extrato (ex: 1.037)")
    moisture_pct    = models.FloatField(null=True, blank=True,
                                        validators=[MinValueValidator(0), MaxValueValidator(100)])
    notes           = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.color_ebc} EBC)"

    class Meta:
        ordering = ['name']


#   Lupulos 
#─────────────────────────────────────────────
class Hop(models.Model):
    """Variedade de lúpulo com dados de alfa/beta ácido."""
    TYPE_CHOICES = [
        ('bittering', 'Amargor'),
        ('aroma', 'Aroma'),
        ('dual', 'Duplo Propósito'),
    ]
    FORM_CHOICES = [
        ('pellet', 'Pellet'),
        ('whole',  'Flor / Folha'),
        ('plug',   'Plug'),
        ('cryo',   'Cryo / LupuLN2'),
    ]

    name            = models.CharField(max_length=150)
    origin_country  = models.CharField(max_length=100, blank=True)
    hop_type        = models.CharField(max_length=20, choices=TYPE_CHOICES, default='dual')
    form            = models.CharField(max_length=20, choices=FORM_CHOICES, default='pellet')
    alpha_acid_pct  = models.FloatField(help_text="Porcentagem de alfa ácido (ex: 12.5)",
                                        validators=[MinValueValidator(0), MaxValueValidator(100)])
    aroma_profile   = models.TextField(blank=True, help_text="ex: cítrico, tropical")
    notes           = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.alpha_acid_pct}% AA)"

    class Meta:
        ordering = ['name']

#   Fermento
#─────────────────────────────────────────────
class Yeast(models.Model):
    """Cepa de levedura com características de fermentação."""
    TYPE_CHOICES = [
        ('ale',      'Ale'),
        ('lager',    'Lager'),
        ('wheat',    'Trigo / Weizen'),
        ('wild',     'Selvagem / Brett'),
        ('hybrid',   'Híbrida / Kveik'),
        ('other',    'Outra'),
    ]
    name                = models.CharField(max_length=150)
    yeast_type          = models.CharField(max_length=20, choices=TYPE_CHOICES, default='ale')
    temp_min_c          = models.FloatField(help_text="Temperatura mínima de fermentação (°C)")
    temp_max_c          = models.FloatField(help_text="Temperatura máxima de fermentação (°C)")
    flavor_notes        = models.TextField(blank=True)

    class Meta:
        ordering = ['name']


#  RECEITA
# ─────────────────────────────────────────────

class Recipe(models.Model):
    """Receita mestre de cerveja."""
    name         = models.CharField(max_length=200)
    style        = models.ForeignKey(BeerStyle, null=True, blank=True,
                                     on_delete=models.SET_NULL, related_name='recipes')
    description  = models.TextField(blank=True)
    author       = models.CharField(max_length=150, blank=True)

    # ── Volumes & tempos ──────────────────────
    batch_size_l  = models.FloatField(help_text="Volume final do lote em litros",
                                      validators=[MinValueValidator(0.1)])
    boil_volume_l = models.FloatField(help_text="Volume pré-fervura em litros",
                                      validators=[MinValueValidator(0.1)])
    boil_time_min = models.IntegerField(help_text="Duração da fervura em minutos",
                                        validators=[MinValueValidator(0)])
    efficiency_pct = models.FloatField(default=65,
                                       validators=[MinValueValidator(0), MaxValueValidator(100)],
                                       help_text="Eficiência da cervejaria %")

    # ── Métricas da Cerveja ──────────────────────────────
    og  = models.FloatField(help_text="Densidade Original (ex: 1.060)",
                             validators=[MinValueValidator(1.000)])
    fg  = models.FloatField(help_text="Densidade Final (ex: 1.012)",
                             validators=[MinValueValidator(1.000)])
    abv = models.FloatField(help_text="Teor alcoólico %",
                             validators=[MinValueValidator(0)])
    ibu = models.FloatField(help_text="Unidades Internacionais de Amargor",
                             validators=[MinValueValidator(0)])
    ebc = models.FloatField(help_text="Cor em unidades EBC",
                             validators=[MinValueValidator(0)])
    srm = models.FloatField(null=True, blank=True, help_text="Cor em unidades SRM")

    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


#  RECEITA - foreign keys para junção na receita principal
# ─────────────────────────────────────────────

class RecipeMalt(models.Model):
    """Malte/fermentável usado em uma receita com sua quantidade."""
    recipe     = models.ForeignKey(Recipe, related_name='malts', on_delete=models.CASCADE)
    malt       = models.ForeignKey(Malt,   on_delete=models.CASCADE)
    amount_kg  = models.FloatField(validators=[MinValueValidator(0)])
    percentage = models.FloatField(null=True, blank=True,
                                   validators=[MinValueValidator(0), MaxValueValidator(100)],
                                   help_text="% do total de grãos")

    def __str__(self):
        return f"{self.amount_kg}kg {self.malt.name}"

    class Meta:
        ordering = ['-amount_kg']


class RecipeHop(models.Model):
    """Adição de lúpulo em uma receita."""
    USE_CHOICES = [
        ('first_wort', 'Mosto Primário'),
        ('boil',       'Fervura'),
        ('whirlpool',  'Whirlpool'),
        ('dry_hop',    'Dry Hop'),
    ]

    recipe         = models.ForeignKey(Recipe, related_name='hops', on_delete=models.CASCADE)
    hop            = models.ForeignKey(Hop,    on_delete=models.CASCADE)
    amount_g       = models.FloatField(validators=[MinValueValidator(0)])
    use            = models.CharField(max_length=20, choices=USE_CHOICES, default='boil')
    time_min       = models.IntegerField(
        help_text="Minutos antes do fim da fervura (fervura/whirlpool), ou dias (dry hop)",
        validators=[MinValueValidator(0)]
    )
    ibu_contribution = models.FloatField(null=True, blank=True,
                                         help_text="Contribuição calculada de IBU")

    def __str__(self):
        return f"{self.amount_g}g {self.hop.name} @ {self.time_min}min ({self.use})"

    class Meta:
        ordering = ['-time_min']


class RecipeYeast(models.Model):
    """Levedura adicionada em uma receita."""
    recipe        = models.ForeignKey(Recipe, related_name='yeasts', on_delete=models.CASCADE)
    yeast         = models.ForeignKey(Yeast,  on_delete=models.CASCADE)
    amount        = models.FloatField(help_text="Pacotes (dry) ou mL (líquida)",
                                      validators=[MinValueValidator(0)])
    starter       = models.BooleanField(default=False)
    starter_size_l = models.FloatField(null=True, blank=True,
                                       help_text="Volume do starter em litros")

    def __str__(self):
        return f"{self.yeast.name} ×{self.amount}"


# ─────────────────────────────────────────────
#  MASH  PROFILE
# ─────────────────────────────────────────────

class MashStep(models.Model):
    """Etapa da mosturação (ex: repouso proteico, sacarificação, mash-out)."""
    TYPE_CHOICES = [
        ('infusion',    'Infusão'),
        ('decoction',   'Decocção'),
        ('temperature', 'Temperatura (HERMS/RIMS)'),
        ('sparge',      'Lavagem'),
    ]

    recipe     = models.ForeignKey(Recipe, related_name='mash_steps', on_delete=models.CASCADE)
    name       = models.CharField(max_length=100, help_text="ex: Repouso de Sacarificação")
    step_type  = models.CharField(max_length=20, choices=TYPE_CHOICES, default='infusion')
    temp_c     = models.FloatField(help_text="Temperatura alvo em °C")
    time_min   = models.IntegerField(help_text="Tempo de repouso em minutos",
                                     validators=[MinValueValidator(0)])
    water_temp_c = models.FloatField(null=True, blank=True,
                                     help_text="Temperatura da água de infusão (°C)")
    order      = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.order}. {self.name} – {self.temp_c}°C × {self.time_min}min"

    class Meta:
        ordering = ['order']


# Perfil de Fermentação 
# ─────────────────────────────────────────────

class FermentationStep(models.Model):
    """Uma etapa do cronograma de fermentação (primária, secundária, lagering, etc)."""
    STAGE_CHOICES = [
        ('primary',      'Fermentação Primária'),
        ('secondary',    'Secundária / Condicionamento'),
        ('dry_hop',      'Repouso Dry Hop'),
        ('lagering',     'Lagering / Cold Crash'),
        ('carbonation',  'Carbonatação'),
    ]

    recipe      = models.ForeignKey(Recipe, related_name='fermentation_steps',
                                    on_delete=models.CASCADE)
    stage       = models.CharField(max_length=20, choices=STAGE_CHOICES, default='primary')
    temp_c      = models.FloatField(help_text="Temperatura em °C")
    duration_days = models.IntegerField(help_text="Duração em dias",
                                        validators=[MinValueValidator(0)])
    notes       = models.TextField(blank=True)
    order       = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.order}. {self.get_stage_display()} – {self.temp_c}°C × {self.duration_days}d"

    class Meta:
        ordering = ['order']



#  Perfil da água
# ─────────────────────────────────────────────

class WaterProfile(models.Model):
    """Perfil de química da água alvo para uma receita."""
    recipe      = models.OneToOneField(Recipe, related_name='water_profile',
                                       on_delete=models.CASCADE)
    # Íons em ppm (mg/L)
    calcium_ppm     = models.FloatField(default=0)
    magnesium_ppm   = models.FloatField(default=0)
    sodium_ppm      = models.FloatField(default=0)
    chloride_ppm    = models.FloatField(default=0)
    sulfate_ppm     = models.FloatField(default=0)
    bicarbonate_ppm = models.FloatField(default=0)
    ph              = models.FloatField(null=True, blank=True,
                                        validators=[MinValueValidator(0), MaxValueValidator(14)],
                                        help_text="pH alvo do mosto")

    def __str__(self):
        return f"Water profile for {self.recipe.name}"
