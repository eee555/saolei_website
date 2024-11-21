import { ElNotification } from "element-plus";
import { local } from "@/store";

export const copyToClipboard = async (str: string) => {
    try {
        await navigator.clipboard.writeText(str);
        ElNotification({
            title: '复制成功！',
            type: 'success',
            duration: local.notification_duration,
        });
    } catch(err) {
        ElNotification({
            title: '复制失败！',
            type: 'error',
            duration: local.notification_duration,
        })
    }
}
