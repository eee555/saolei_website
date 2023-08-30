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




