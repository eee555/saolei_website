import { computed } from 'vue';

import { colorTheme } from '.';

import { PiecewiseColorScheme } from '@/utils/colors';

const stnbTheme = computed(() => PiecewiseColorScheme.createFromTheme(colorTheme.value.stnb));
const ioeTheme = computed(() => PiecewiseColorScheme.createFromTheme(colorTheme.value.ioe));
const bvsTheme = computed(() => PiecewiseColorScheme.createFromTheme(colorTheme.value.bvs));
const etimeTheme = computed(() => PiecewiseColorScheme.createFromTheme(colorTheme.value.etime));
const itimeTheme = computed(() => PiecewiseColorScheme.createFromTheme(colorTheme.value.itime));
const btimeTheme = computed(() => PiecewiseColorScheme.createFromTheme(colorTheme.value.btime));

export const colorThemes = {
    stnb: stnbTheme,
    ioe: ioeTheme,
    bvs: bvsTheme,
    etime: etimeTheme,
    itime: itimeTheme,
    btime: btimeTheme,
};
