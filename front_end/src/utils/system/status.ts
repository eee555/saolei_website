import { ElNotification } from "element-plus"

import { httpResponseType, httpResponseMessage, httpResponseTitle } from "../common/HttpResponse";

export function generalNotification(t: any, status: number, action: string) {
    let type = Math.floor(status / 100);
    ElNotification({
        title: t.t(httpResponseTitle[type], [action]),
        message: t.t(httpResponseMessage[status]),
        type: httpResponseType[type],
        duration: localStorage.getItem('local').notification_duration, 
    })
}
