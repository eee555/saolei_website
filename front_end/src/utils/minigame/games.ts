import version from '../../../local-minigame/version.json';

export const trainingGames = ['left-click', 'flag-chord', 'missing-cell'] as const;
export type TrainingGame = typeof trainingGames[number];
export const offlineDownloadFilename = `OpenMinesweeperMinigames-${version.version}.zip`;
export const offlineDownloadUrl = `${import.meta.env.BASE_URL}assets/${offlineDownloadFilename}`;
