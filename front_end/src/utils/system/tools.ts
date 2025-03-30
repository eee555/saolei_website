
// import useLogStore from '@/store/system-log'
import { ElMessage } from 'element-plus'
// import Log from '../common/log.print'

/**
 * @description 把时间戳从UTC转为当地时间
 * @param {String} t 需要转换的时间戳
 */
export function utc_to_local_format(t = '2024-01-10T14:03:09Z') {
    const utc_time = new Date(t);
    return utc_time.toLocaleString('default', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
    }).replace(/\//g, '-');
}

// credit: https://stackoverflow.com/a/5767357/12144822
export function removeItem<T>(arr: Array<T>, value: T): Array<T> {
    const index = arr.indexOf(value);
    if (index > -1) {
        arr.splice(index, 1);
    }
    return arr;
}

/**
 * @description 安全地解析 json 字符串
 * @param {String} jsonString 需要解析的 json 字符串
 * @param {String} defaultValue 默认值
 */
export function parse(jsonString = '{}', defaultValue = {}) {
    let result = defaultValue
    try {
        result = JSON.parse(jsonString)
    } catch (error) {
        console.log(error)
    }
    return result
}

/**
 * @description 接口请求返回
 * @param {Any} data 返回值
 * @param {String} msg 状态信息
 * @param {Number} code 状态码
 */
export function response(data = {}, msg = '', code = 0) {
    return [
        200,
        { code, msg, data },
    ]
}

/**
 * @description 接口请求返回 正确返回
 * @param {Any} data 返回值
 * @param {String} msg 状态信息
 */
export function responseSuccess(data = {}, msg = '成功') {
    return response(data, msg)
}

/**
 * @description 接口请求返回 错误返回
 * @param {Any} data 返回值
 * @param {String} msg 状态信息
 * @param {Number} code 状态码
 */
export function responseError(data = {}, msg = '请求失败', code = 500) {
    return response(data, msg, code)
}

/**
 * @description 记录和显示错误
 * @param {Error} error 错误对象
 */
export function errorLog(error: Error) {
    // 添加到日志
    // const logStore = useLogStore()
    // logStore.push( {
    //   message: '数据请求异常',
    //   type: 'danger',
    //   meta: {
    //     error
    //   }
    // })
    // 打印到控制台
    if (import.meta.env.NODE_ENV === 'development') {
    // Log.danger('>>>>>> Error >>>>>>')
        console.log(error)
    }
    // 显示提示
    ElMessage.error({
        message: error.message,
        duration: 5 * 1000,
    })
}

/**
 * @description 创建一个错误
 * @param {String} msg 错误信息
 */
export function errorCreate(msg: string | undefined) {
    const error = new Error(msg)
    errorLog(error)
    throw error
}

/**
 * @description 数据404消息提示
 * @param {String} msg 错误信息
 */
export function dataNotFound(msg: string | undefined) {
    // 显示提示
    ElMessage.info({
        message: msg,
        duration: 5 * 1000,
    })
}

/**
 * @description 数据请求成功
 * @param {String} msg 成功信息
 */
export function successMsg(msg: string | undefined) {
    ElMessage.success({
        message: msg,
        duration: 5 * 1000,
    })
}
