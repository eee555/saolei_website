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

interface ExtendedVideoStat {
    left: number,
    right: number,
    double: number,
    cl: number,
    left_s: number,
    right_s: number,
    double_s: number,
    cl_s: number,
    path: number,
    flag: number,
    flag_s: number,
    stnb: number,
    rqp: number,
    ioe: number,
    thrp: number,
    corr: number,
    ce: number,
    ce_s: number,
    op: number,
    isl: number,
    cell0: number,
    cell1: number,
    cell2: number,
    cell3: number,
    cell4: number,
    cell5: number,
    cell6: number,
    cell7: number,
    cell8: number,
}

interface VideoStat {
    level: string,
    mode: string,
    timems: number,
    bbbv: number,
    identifier: string,
    review_code: number,
}

export interface GeneralFile {
    uid: number,
    id: number,
    filename: string,
    file: File,
    status: string,
    videostat: VideoStat | null,
    extstat: ExtendedVideoStat | null,
}
