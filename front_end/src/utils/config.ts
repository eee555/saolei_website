
const ArbiterStatsAutoColorTemplate = [
    'rgba(255,255,255,0)',
    '#808080', '#595959', '#AE78D6', '#7030A0', // 1
    '#FF5B5B', '#FFA7A7', '#FF0000', '#BC0000', // 2
    '#92D050', '#B2DE82', '#00B050', '#009242', // 3
    '#00B0F0', '#81DEFF', '#0070C0', '#005696', // 4
    '#FFC000', '#FFE07D', '#E7831D', '#A65C12', // 5
    '#FF57B7', '#FF97D2', '#D6007B', '#A2005D', // 6
    '#14D2A0', '#7DF3D4', '#0F9D78', '#0B7B5E', // 7
    '#CCFF66',
];

const ArbiterStatsAutoValueTemplate = [
    0.01,
    0.5, 1, 1.5, 2,
    2.25, 2.5, 2.75, 3,
    3.25, 3.5, 3.75, 4,
    4.25, 4.5, 4.75, 5,
    5.25, 5.5, 5.75, 6,
    6.25, 6.5, 6.75, 7,
    7.25, 7.5, 7.75, 8,
];

const ArbiterStatsAutoValueTemplate_IOE = [
    0.01,
    0.5, 0.6, 0.7, 0.8,
    0.9, 0.95, 1, 1.05,
    1.1, 1.15, 1.2, 1.25,
    1.3, 1.35, 1.4, 1.45,
    1.5, 1.55, 1.6, 1.65,
    1.7, 1.75, 1.8, 1.85,
    1.9, 1.95, 2, 2.1,
];

export const colorSchemeTemplates = {
    ArbiterStatsAuto: {
        bvs: {
            thresholds: ArbiterStatsAutoValueTemplate,
            colors: ArbiterStatsAutoColorTemplate,
        },
        stnb: {
            thresholds: ArbiterStatsAutoValueTemplate.map((v) => v * 25),
            colors: ArbiterStatsAutoColorTemplate,
        },
        ioe: {
            thresholds: ArbiterStatsAutoValueTemplate_IOE,
            colors: ArbiterStatsAutoColorTemplate,
        },
        btime: {
            thresholds: ArbiterStatsAutoValueTemplate.map((v) => 12 - v * 2).reverse(),
            colors: ArbiterStatsAutoColorTemplate.toReversed(),
        },
        itime: {
            thresholds: ArbiterStatsAutoValueTemplate.map((v) => 30 - v * 4).reverse(),
            colors: ArbiterStatsAutoColorTemplate.toReversed(),
        },
        etime: {
            thresholds: ArbiterStatsAutoValueTemplate.map((v) => 90 - v * 10).reverse(),
            colors: ArbiterStatsAutoColorTemplate.toReversed(),
        },
    },
};
