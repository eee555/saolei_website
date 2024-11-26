import { ElNotification } from "element-plus";
import { local } from "@/store";
import i18n from "@/i18n";
// @ts-ignore
const { t } = i18n.global;

export const copyToClipboard = async (str: string) => {
    try {
        await navigator.clipboard.writeText(str);
        ElNotification({
            title: t('msg.copyToClipboardSuccess'),
            type: 'success',
            duration: local.notification_duration,
        });
    } catch(err) {
        ElNotification({
            title: t('msg.copyToClipboardFail'),
            type: 'error',
            duration: local.notification_duration,
        })
    }
}
