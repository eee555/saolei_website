export interface DbSchema {
    sys: {},
    database: {}
}
export interface dbAcceptParma {
    dbName: string,
    path: string,
    value: boolean | string,
    user: boolean
}
export enum LoginStatus {
    // 首次打开页面，还没有做判断，判断是否需要尝试登录，主要是防抖用
    Undefined,
    // 登录成功了
    IsLogin,
    // 未登录状态
    NotLogin,
    // 正在打开弹窗填写登录信息
    Login,
    // 正在打开弹窗填写注册信息
    Register,
    // 正在弹窗上找回密码
    IsRetrieve,
}

export interface RecordBIE {
    timems: number[],
    bvs: number[],
    stnb: number[],
    ioe: number[],
    path: number[],
    timems_id: number[],
    bvs_id: number[],
    stnb_id: number[],
    ioe_id: number[],
    path_id: number[],
}

export interface Record {
    timems: number,
    bvs: number,
    stnb: number,
    ioe: number,
    path: number,
    timems_id: number,
    bvs_id: number,
    stnb_id: number,
    ioe_id: number,
    path_id: number,
}
