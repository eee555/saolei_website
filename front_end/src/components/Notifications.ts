import { ElNotification } from 'element-plus';

import i18n from '@/i18n';
import { local } from '@/store';

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

export function baseErrorNotification(title: string, message: string) {
    ElNotification({
        title: title,
        message: message,
        type: 'error',
        duration: local.value.notification_duration,
    });
}

export function httpErrorNotification(error: any) {
    const status = error.response.status;
    if (status in notificationMessage) {
        baseErrorNotification(t('msg.actionFail'), t(notificationMessage[status]));
    } else {
        unknownErrorNotification(error);
    }
}

export function successNotification(response: any) {
    if (response.status == 200) {
        ElNotification({
            title: t('msg.actionSuccess'),
            type: 'success',
            duration: local.value.notification_duration,
        });
    } else {
        unknownErrorNotification(response);
    }
}

export function unknownErrorNotification(error: any) {
    baseErrorNotification(t('msg.unknownError'), error);
}

export function generalErrorNotification(object: string, category: string) {
    baseErrorNotification(t(`errorMsg.${object}.title`), t(`errorMsg.${object}.${category}`));
}
