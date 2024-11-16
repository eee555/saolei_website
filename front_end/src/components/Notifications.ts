import { local } from "@/store";
import { ElNotification } from "element-plus";
import i18n from "@/i18n";

// @ts-ignore
const { t } = i18n.global;

const notificationMessage: { [code: number]: string } = {
    200: 'common.response.OK',
    400: 'common.response.BadRequest',
    403: 'common.response.Forbidden',
    404: 'common.response.NotFound',
    413: 'common.response.PayloadTooLarge',
    415: 'common.response.UnsupportedMediaType',
    429: 'common.response.TooManyRequests',
    500: 'common.response.InternalServerError',
};

export const httpErrorNotification = (error: any) => {
    let status = error.response.status
    if (status in notificationMessage) {
        ElNotification({
            title: t('msg.actionFail'),
            message: t(notificationMessage[status]),
            type: 'error',
            duration: local.notification_duration,
        })
    } else {
        unknownErrorNotification(error)
    }

}

export const successNotification = (response: any) => {
    if (response.status == 200) {
        ElNotification({
            title: t('msg.actionSuccess'),
            type: 'success',
            duration: local.notification_duration,
        })
    } else {
        unknownErrorNotification(response)
    }

}

export const unknownErrorNotification = (error: any) => {
    ElNotification({
        title: t('msg.unknownError'),
        message: error,
        type: 'error',
        duration: local.notification_duration,
    })
}