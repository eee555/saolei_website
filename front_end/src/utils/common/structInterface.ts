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
    // 登录成功了
    IsLogin,
    // 未登录状态
    NotLogin,
    // 正在弹窗上登录
    Login,
    // 正在弹窗上注册
    Register,
    // 正在弹窗上找回密码
    IsRetrieve
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



