import { useLocalStore } from "@/store";
import { ElNotification } from "element-plus"
const local = useLocalStore();

const notificationType = ['', 'success', 'error'];
const notificationTitle = ['', 'common.msg.actionSuccess', 'common.msg.actionFail'];
const notificationMessage: { [code: number]: string} = {
    100: '',
    200: 'common.msg.unknownError',
    201: 'common.msg.permissionDenied',
    202: 'common.msg.backendError',
    203: 'common.msg.unrecognisedRequest',
};

export function generalNotification(t: any, status: number, action: string) {
    let type = Math.floor(status / 100);
    ElNotification({
        title: t.t(notificationTitle[type], [action]),
        message: t.t(notificationMessage[status]),
        type: notificationType[type],
        duration: local.notification_duration,
    })
}