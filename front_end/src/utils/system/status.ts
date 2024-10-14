import { ElNotification } from "element-plus"

const notificationType = ['', '', 'success', '', 'error', 'error'];
const notificationTitle = ['', '', 'common.msg.actionSuccess', '', 'common.msg.actionFail', 'common.msg.actionFail'];
const notificationMessage: { [code: number]: string} = {
    200: 'common.response.OK',
    400: 'common.response.BadRequest',
    403: 'common.response.Forbidden',
    404: 'common.response.NotFound',
    413: 'common.response.PayloadTooLarge',
    415: 'common.response.UnsupportedMediaType',
    429: 'common.response.TooManyRequests',
    500: 'common.response.InternalServerError',
};

export function generalNotification(t: any, status: number, action: string) {
    let type = Math.floor(status / 100);
    let local = localStorage.getItem('local')
    let duration = 4500
    if (local !== null) duration = JSON.parse(local).notification_duration
    ElNotification({
        title: t.t(notificationTitle[type], [action]),
        message: t.t(notificationMessage[status]),
        type: notificationType[type],
        duration: duration,
    })
}

export function unknownErrorNotification(t: any) {
    ElNotification({
        title: t.t('common.msg.unknownError'),
        message: t.t('common.msg.contactDeveloper'),
        type: 'error',
        duration: JSON.parse(localStorage.getItem('local')).notification_duration,
    })
}
