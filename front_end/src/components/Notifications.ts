import type { AxiosError, AxiosResponse } from 'axios';
import { ElNotification } from 'element-plus';

import i18n from '@/i18n';
import { local } from '@/store';

const { t } = i18n.global;

const notificationMessage: Record<number, string> = {
    200: 'common.response.OK',
    400: 'common.response.BadRequest',
    403: 'common.response.Forbidden',
    404: 'common.response.NotFound',
    413: 'common.response.PayloadTooLarge',
    415: 'common.response.UnsupportedMediaType',
    429: 'common.response.TooManyRequests',
    500: 'common.response.InternalServerError',
};

export function baseErrorNotification(title: string, message: string): void {
    ElNotification({
        title: title,
        message: message,
        type: 'error',
        duration: local.value.notification_duration,
    });
}

export function httpErrorNotification(error: AxiosError): void {
    const status = error.response?.status;
    if (status !== undefined && status in notificationMessage) {
        baseErrorNotification(t('msg.actionFail'), t(notificationMessage[status]));
    } else {
        unknownErrorNotification(error);
    }
}

export function successNotification(response: AxiosResponse): void {
    if (response.status === 200) {
        ElNotification({
            title: t('msg.actionSuccess'),
            type: 'success',
            duration: local.value.notification_duration,
        });
    } else {
        unknownErrorNotification(response);
    }
}

export function unknownErrorNotification(error: unknown): void {
    baseErrorNotification(t('msg.unknownError'), String(error));
}

export function generalErrorNotification(object: string, category: string): void {
    baseErrorNotification(t(`errorMsg.${object}.title`), t(`errorMsg.${object}.${category}`));
}
