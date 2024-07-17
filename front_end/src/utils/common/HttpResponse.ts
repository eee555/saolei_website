export const httpResponseType = ['', '', 'success', '', 'error', 'error'];
export const httpResponseTitle = ['', '', 'common.msg.actionSuccess', '', 'common.msg.actionFail', 'common.msg.actionFail'];
export const httpResponseMessage: { [code: number]: string} = {
    200: 'common.response.OK',
    400: 'common.response.BadRequest',
    403: 'common.response.Forbidden',
    404: 'common.response.NotFound',
    413: 'common.response.PayloadTooLarge',
    415: 'common.response.UnsupportedMediaType',
    429: 'common.response.TooManyRequests',
    500: 'common.response.InternalServerError',
};