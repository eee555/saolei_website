import { afterEach, describe, expect, it, vi } from 'vitest';
import { effectScope } from 'vue';
import type { EffectScope } from 'vue';

import { useLocalReplaySource } from './useLocalReplaySource';

const scopes: EffectScope[] = [];
function setup() {
    const scope = effectScope();
    scopes.push(scope);
    const state = scope.run(useLocalReplaySource);
    if (!state) throw new Error('Expected file source state');
    return { scope, ...state };
}
afterEach(() => {
    scopes.splice(0).forEach((scope) => {
        scope.stop();
    });
    vi.restoreAllMocks();
});

describe('local replay input', () => {
    it.each([['AVF', 'a'], ['EVF', 'e'], ['MVF', 'm'], ['RMV', 'r']])('reads %s as %s without parsing or changing the bytes', async (extension, software) => {
        const state = setup();
        const file = new File([new Uint8Array([1, 2, 3])], `录像.${extension}`);
        await state.selectFiles([file]);
        expect(state.source.value?.software).toBe(software);
        expect(state.source.value?.filename).toBe(file.name);
        expect(new Uint8Array(state.source.value?.data ?? new ArrayBuffer(0))).toEqual(new Uint8Array([1, 2, 3]));
        expect(state.loading.value).toBe(false);
        expect(state.errorMessage.value).toBe('');
    });

    it('ignores a late read after a newer selection or disposal', async () => {
        const state = setup();
        const first = new File(['first'], 'first.evf');
        let finish: (buffer: ArrayBuffer) => void = () => {
            throw new Error('Read not started');
        };
        vi.spyOn(first, 'arrayBuffer').mockReturnValue(new Promise((resolve) => {
            finish = resolve;
        }));
        const pending = state.selectFiles([first]);
        await state.selectFiles([new File(['second'], 'second.avf')]);
        finish(new ArrayBuffer(1));
        await pending;
        expect(state.source.value?.filename).toBe('second.avf');
        const pendingUnmount = state.selectFiles([first]);
        state.scope.stop();
        await pendingUnmount;
        expect(state.source.value).toBeNull();
    });

    it('rejects unsupported and multiple files, reports reading errors and recovers', async () => {
        const state = setup();
        await state.selectFiles([new File(['bad'], 'bad.zip')]);
        expect(state.errorMessage.value).toBe('unsupportedFormat');
        await state.selectFiles([new File(['a'], 'a.evf'), new File(['b'], 'b.evf')]);
        expect(state.errorMessage.value).toBe('oneFileOnly');
        const bad = new File(['bad'], 'bad.evf');
        vi.spyOn(bad, 'arrayBuffer').mockRejectedValue(new Error('Read failed'));
        await state.selectFiles([bad]);
        expect(state.errorMessage.value).toBe('Read failed');
        expect(state.source.value).toBeNull();
        expect(state.loading.value).toBe(false);
        await state.selectFiles([new File(['good'], 'good.evf')]);
        expect(state.errorMessage.value).toBe('');
        expect(state.source.value?.filename).toBe('good.evf');
        await state.selectFiles([]);
        expect(state.source.value?.filename).toBe('good.evf');
    });
});
