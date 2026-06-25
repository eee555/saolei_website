import { ElWatermark } from 'element-plus';
import type { Directive } from 'vue';
import { h, render, watchEffect } from 'vue';

import i18n from '@/i18n';
import { local } from '@/store';

const { t } = i18n.global;

type ExperimentalFeatureElement = HTMLElement & {
    _watermarkCleanup?: () => void;
};

export const vExperimental: Directive<HTMLElement> = {
    mounted(el) {
        if (getComputedStyle(el).position === 'static') {
            el.style.position = 'relative';
        }

        const placeholder = document.createComment('experimental-feature');
        const container = document.createElement('div');
        Object.assign(container.style, {
            position: 'absolute',
            inset: '0',
            pointerEvents: 'none',
        });

        el.appendChild(container);
        el.parentNode?.insertBefore(placeholder, el);

        const stop = watchEffect(() => {
            if (local.value.experimental) {
                if (!el.parentNode) {
                    placeholder.parentNode?.insertBefore(el, placeholder.nextSibling);
                }
                render(
                    h(ElWatermark, {
                        content: t('experimentalFeature'),
                        font: { color: 'rgba(255,0,0,0.3)', fontSize: 50 },
                        style: { width: '100%', height: '100%' },
                    }),
                    container,
                );
                return;
            }

            render(null, container);
            el.remove();
        });

        (el as ExperimentalFeatureElement)._watermarkCleanup = () => {
            stop();
            render(null, container);
            container.remove();
            placeholder.remove();
        };
    },

    unmounted(el) {
        (el as ExperimentalFeatureElement)._watermarkCleanup?.();
        delete (el as ExperimentalFeatureElement)._watermarkCleanup;
    },
};
