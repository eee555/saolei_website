/*
关于 VideoStat 和 UploadVideoForm
这两个类型有非常大的重叠，但是无法共用代码。VideoStat 用于提供给前端进行可视化，UploadVideoForm 储存的是发送给后端的表单，两个需求随时可能失去同步。
*/

import { UploadRawFile } from "element-plus";
import { AvfVideo, EvfVideo } from "ms-toollib";

export function load_video_file(stream: Uint8Array, filename: string) {
    const ext = filename.slice(-3);
    let video: AvfVideo | EvfVideo;
    if (ext === 'avf') {
        video = AvfVideo.new(stream, filename);
    } else if (ext === 'evf') {
        video = EvfVideo.new(stream, filename);
    } else return null;
    video.parse_video();
    video.analyse();
    return video;
}

export async function upload_prepare(file: UploadRawFile) {
    let file_u8 = new Uint8Array(await file.arrayBuffer());
    let video = load_video_file(file_u8, file.name);
    let status = 'pass';
    if (video === null) {
        status = 'fileext';
    }
    return {
        index: 0,
        filename: file.name,
        status: status,
        stat: extract_stat(video),
        form: upload_form(file, video),
    }
}

export interface VideoStat {
    id: number,
    level: string,
    mode: string,
    timems: number,
    bv: number,
    bvs: number,
    review_code: number,
    identifier: string,
    left: number,
    right: number,
    double: number,
    left_ce: number,
    right_ce: number,
    double_ce: number,
    path: number,
    flag: number,
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

export function extract_stat(video: AvfVideo | EvfVideo | null): VideoStat | null {
    if (video === null) return null;
    const decoder = new TextDecoder();
    video.current_time = 1e8;
    return {
        id: 0,
        level: ["b", "i", "e", "c"][video.get_level - 3],
        mode: String(video.get_mode).padStart(2, '0'),
        timems: video.get_rtime_ms,
        bv: video.get_bbbv,
        bvs: video.get_bbbv_s,
        identifier: decoder.decode(video.get_player_identifier),
        review_code: video.is_valid(),
        left: video.get_left,
        right: video.get_right,
        double: video.get_double,
        left_ce: video.get_lce,
        right_ce: video.get_rce,
        double_ce: video.get_dce,
        path: video.get_path,
        flag: video.get_flag,
        op: video.get_op,
        isl: video.get_isl,
        cell0: video.get_cell0,
        cell1: video.get_cell1,
        cell2: video.get_cell2,
        cell3: video.get_cell3,
        cell4: video.get_cell4,
        cell5: video.get_cell5,
        cell6: video.get_cell6,
        cell7: video.get_cell7,
        cell8: video.get_cell8,
    };
}

export interface UploadVideoForm {
    file: File,
    review_code: number,
    identifier: string,

    software: string,
    level: string,
    mode: string,
    timems: number,
    bv: number,
    left: number,
    right: number,
    double: number,
    left_ce: number,
    right_ce: number,
    double_ce: number,
    path: number,
    flag: number,
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

    // to be discarded
    left_s: number,
    right_s: number,
    double_s: number,
    flag_s: number,
    cl: number,
    cl_s: number,
    ce: number,
    ce_s: number,
    stnb: number,
    rqp: number,
    ioe: number,
    corr: number,
    thrp: number,
}

export function upload_form(file: UploadRawFile, video: AvfVideo | EvfVideo | null): UploadVideoForm | null {
    let software;
    if (video instanceof AvfVideo) software = "a";
    else if (video instanceof EvfVideo) software = "e";
    else return null;
    const decoder = new TextDecoder();
    video.current_time = 1e8;
    return {
        file: file,
        review_code: video.is_valid(),
        identifier: decoder.decode(video.get_player_identifier),

        software: software,
        level: ["b", "i", "e", "c"][video.get_level - 3],
        mode: String(video.get_mode).padStart(2, '0'),
        timems: video.get_rtime_ms,
        bv: video.get_bbbv,
        left: video.get_left,
        right: video.get_right,
        double: video.get_double,
        left_ce: video.get_lce,
        right_ce: video.get_rce,
        double_ce: video.get_dce,
        path: video.get_path,
        flag: video.get_flag,
        op: video.get_op,
        isl: video.get_isl,
        cell0: video.get_cell0,
        cell1: video.get_cell1,
        cell2: video.get_cell2,
        cell3: video.get_cell3,
        cell4: video.get_cell4,
        cell5: video.get_cell5,
        cell6: video.get_cell6,
        cell7: video.get_cell7,
        cell8: video.get_cell8,

        left_s: video.get_left_s,
        right_s: video.get_right_s,
        double_s: video.get_double_s,
        flag_s: video.get_flag_s,
        cl: video.get_cl,
        cl_s: video.get_cl_s,
        ce: video.get_ce,
        ce_s: video.get_ce_s,
        stnb: video.get_stnb,
        rqp: video.get_rqp,
        ioe: video.get_ioe,
        corr: video.get_corr,
        thrp: video.get_thrp,
    }
}

export function get_upload_status(file: UploadRawFile, video: AvfVideo | EvfVideo | null, identifiers: Array<string>) {
    const decoder = new TextDecoder();
    if (video === null) return "unsupported";
    if (video.get_level == 6) return "custom";
    if (file.name.length >= 100) return "filename";
    if (video.is_valid() == 1) return "invalid";
    if (video.is_valid() == 3) return "needApprove";
    if (!identifiers.includes(decoder.decode(video.get_player_identifier))) return "identifier";
    return "pass";
}