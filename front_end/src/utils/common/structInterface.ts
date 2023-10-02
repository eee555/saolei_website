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
    IsLogin,
    NotLogin,
    Login,
    Register
}

export interface RecordBIE {
    time: number[],
    bvs: number[],
    stnb: number[],
    ioe: number[],
    path: number[],
    time_id: number[],
    bvs_id: number[],
    stnb_id: number[],
    ioe_id: number[],
    path_id: number[],
}

export interface Record {
    time: number,
    bvs: number,
    stnb: number,
    ioe: number,
    path: number,
    time_id: number,
    bvs_id: number,
    stnb_id: number,
    ioe_id: number,
    path_id: number,
}



