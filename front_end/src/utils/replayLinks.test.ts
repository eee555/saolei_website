import { afterEach, describe, expect, it, vi } from 'vitest';

import { getReplayPreviewUrl, getStrangeDustAnalyzerUrl } from './replayLinks';

afterEach(() => vi.unstubAllEnvs());

describe('external replay links', () => {
    it.each([['a', 'avf'], ['e', 'evf'], ['m', 'mvf'], ['r', 'rmv']] as const)('passes the %s replay URL to StrangeDust without changing the filename', (software, extension) => {
        vi.stubEnv('VITE_BASE_API', 'https://openms.top');
        const replayUrl = getReplayPreviewUrl(42, software);
        expect(replayUrl).toBe(`https://openms.top/api/video/preview?id=42.${extension}`);
        const analyzer = new URL(getStrangeDustAnalyzerUrl(replayUrl));
        expect(analyzer.origin + analyzer.pathname).toBe('https://strange-dust.github.io/minesweeper-replay-analyzer/');
        expect(analyzer.searchParams.get('replay')).toBe(replayUrl);
        expect([...analyzer.searchParams.keys()]).toEqual(['replay']);
    });

    it('encodes the inner filename and preserves inner query parameters and fragments', () => {
        vi.stubEnv('VITE_BASE_API', 'https://openms.top');
        const preview = new URL(getReplayPreviewUrl('a&b', 'e'));
        expect(preview.searchParams.get('id')).toBe('a&b.evf');
        expect([...preview.searchParams.keys()]).toEqual(['id']);
        const replayUrl = `${preview.href}&name=${encodeURIComponent('原始录像.evf')}#frame`;
        const analyzer = new URL(getStrangeDustAnalyzerUrl(replayUrl));
        expect(analyzer.searchParams.get('replay')).toBe(replayUrl);
        expect([...analyzer.searchParams.keys()]).toEqual(['replay']);
        expect(analyzer.hash).toBe('');
    });
});
