import { useLocalStore } from "@/store";
import { ElNotification } from "element-plus"
const local = useLocalStore();

const notificationType = ['', '', 'success', '', 'error', 'error'];
const notificationTitle = ['', '', 'common.msg.actionSuccess', '', 'common.msg.actionFail', 'common.msg.actionFail'];
const notificationMessage: { [code: number]: string} = {
    200: 'common.response.OK',
    400: 'common.response.BadRequest',
    403: 'common.response.Forbidden',
    404: 'common.response.NotFound',
    413: 'common.response.PayloadTooLarge',
    415: 'common.response.UnsupportedMediaType',
    500: 'common.response.InternalServerError',
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
