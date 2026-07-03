from config.text_choices import MS_TextChoices

CUSTOM_PLUCK_CONFIGS = {
    MS_TextChoices.Level.CUSTOM_8_8_40: (8, 8, 40),
    MS_TextChoices.Level.CUSTOM_16_16_100: (16, 16, 100),
    MS_TextChoices.Level.CUSTOM_16_30_150: (16, 30, 150),
    MS_TextChoices.Level.CUSTOM_24_30_200: (24, 30, 200),
}

CUSTOM_PLUCK_LEVELS = set(CUSTOM_PLUCK_CONFIGS)
CUSTOM_PLUCK_MODES = {
    MS_TextChoices.Mode.STD,
    MS_TextChoices.Mode.NF,
    MS_TextChoices.Mode.RKC,
}
