from config.text_choices import MS_TextChoices

CUSTOM_PLUCK_CONFIGS = {
    MS_TextChoices.Level.CUSTOM_8_8_20: (8, 8, 20),
    MS_TextChoices.Level.CUSTOM_8_8_24: (8, 8, 24),
    MS_TextChoices.Level.CUSTOM_8_8_28: (8, 8, 28),
    MS_TextChoices.Level.CUSTOM_8_8_32: (8, 8, 32),
    MS_TextChoices.Level.CUSTOM_8_8_36: (8, 8, 36),
    MS_TextChoices.Level.CUSTOM_8_8_40: (8, 8, 40),
    MS_TextChoices.Level.CUSTOM_16_16_64: (16, 16, 64),
    MS_TextChoices.Level.CUSTOM_16_16_80: (16, 16, 80),
    MS_TextChoices.Level.CUSTOM_16_16_96: (16, 16, 96),
    MS_TextChoices.Level.CUSTOM_16_16_112: (16, 16, 112),
    MS_TextChoices.Level.CUSTOM_16_16_128: (16, 16, 128),
    MS_TextChoices.Level.CUSTOM_16_30_120: (16, 30, 120),
    MS_TextChoices.Level.CUSTOM_16_30_144: (16, 30, 144),
    MS_TextChoices.Level.CUSTOM_16_30_168: (16, 30, 168),
    MS_TextChoices.Level.CUSTOM_16_30_192: (16, 30, 192),
    MS_TextChoices.Level.CUSTOM_24_30_180: (24, 30, 180),
    MS_TextChoices.Level.CUSTOM_24_30_216: (24, 30, 216),
    MS_TextChoices.Level.CUSTOM_24_30_252: (24, 30, 252),
    MS_TextChoices.Level.CUSTOM_48_64_777: (48, 64, 777),
}

CUSTOM_PLUCK_LEVELS = set(CUSTOM_PLUCK_CONFIGS)
CUSTOM_PLUCK_MODES = {
    MS_TextChoices.Mode.STD,
    MS_TextChoices.Mode.NF,
    MS_TextChoices.Mode.RKC,
}
CUSTOM_PLUCK_CACHE_SIZE = 100
