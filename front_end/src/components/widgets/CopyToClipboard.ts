import { ElNotification } from 'element-plus';

import i18n from '@/i18n';
import { local } from '@/store';

const { t } = i18n.global;

export async function copyToClipboard(str: string): Promise<void> {
    try {
        await navigator.clipboard.writeText(str);
        ElNotification({
            title: t('msg.copyToClipboardSuccess'),
            type: 'success',
            duration: local.value.notification_duration,
        });
    } catch (err) {
        ElNotification({
            title: t('msg.copyToClipboardFail'),
            type: 'error',
            duration: local.value.notification_duration,
        });
        throw err;
    }
}
