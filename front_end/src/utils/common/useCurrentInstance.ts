import type { ComponentInternalInstance } from 'vue';
import { getCurrentInstance } from 'vue';

type GlobalProperties = ComponentInternalInstance['appContext']['config']['globalProperties'];

export default function useCurrentInstance(): { proxy: GlobalProperties } {
    const instance = getCurrentInstance();
    if (instance === null) {
        throw new Error('useCurrentInstance must be called inside component setup.');
    }

    const { appContext } = instance;
    const proxy = appContext.config.globalProperties;
    return {
        proxy,
    };
}

