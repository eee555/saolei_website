/*
关于 VideoStat 和 UploadVideoForm
这两个类型有非常大的重叠，但是无法共用代码。VideoStat 用于提供给前端进行可视化，UploadVideoForm 储存的是发送给后端的表单，两个需求随时可能失去同步。
*/

import { UploadRawFile } from 'element-plus';
import { AvfVideo, EvfVideo, RmvVideo, MvfVideo } from 'ms-toollib';
type AnyVideo = AvfVideo | EvfVideo | RmvVideo | MvfVideo;

export function get_software(video: AnyVideo) {
    if (video instanceof AvfVideo) return 'a';
    else if (video instanceof EvfVideo) return 'e';
    else if (video instanceof RmvVideo) return 'r';
    else return 'm';
}

export function load_video_file(stream: Uint8Array, filename: string) {
    const ext = filename.slice(-3);
    let video: AnyVideo;
    if (ext === 'avf') {
        video = AvfVideo.new(stream, filename);
    } else if (ext === 'evf') {
        video = EvfVideo.new(stream, filename);
    } else if (ext === 'rmv') {
        video = RmvVideo.new(stream, filename);
    } else if (ext === 'mvf') {
        video = MvfVideo.new(stream, filename);
    } else return null;
    video.parse_video();
    video.analyse();
    return video;
}

export async function upload_prepare(file: UploadRawFile) {
    const file_u8 = new Uint8Array(await file.arrayBuffer());
    const video = load_video_file(file_u8, file.name);
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
    };
}

export interface VideoStat {
    id: number;
    level: string;
    mode: string;
    timems: number;
    bv: number;
    bvs: number;
    review_code: number;
    identifier: string;
    left: number;
    right: number;
    double: number;
    left_ce: number;
    right_ce: number;
    double_ce: number;
    path: number;
    flag: number;
    op: number;
    isl: number;
    cell0: number;
    cell1: number;
    cell2: number;
    cell3: number;
    cell4: number;
    cell5: number;
    cell6: number;
    cell7: number;
    cell8: number;
}

export function extract_stat(video: AnyVideo | null): VideoStat | null {
    if (video === null) return null;
    const decoder = new TextDecoder();
    video.current_time = 1e8;
    return {
        id: 0,
        level: ['b', 'i', 'e', 'c'][video.level - 3],
        mode: String(video.mode).padStart(2, '0'),
        timems: video.rtime_ms,
        bv: video.bbbv,
        bvs: video.bbbv_s,
        identifier: decoder.decode(video.player_identifier),
        review_code: video.is_valid(),
        left: video.left,
        right: video.right,
        double: video.double,
        left_ce: video.lce,
        right_ce: video.rce,
        double_ce: video.dce,
        path: video.path,
        flag: video.flag,
        op: video.op,
        isl: video.isl,
        cell0: video.cell0,
        cell1: video.cell1,
        cell2: video.cell2,
        cell3: video.cell3,
        cell4: video.cell4,
        cell5: video.cell5,
        cell6: video.cell6,
        cell7: video.cell7,
        cell8: video.cell8,
    };
}

export interface UploadVideoForm {
    file: File;
}

export function upload_form(file: UploadRawFile, video: AnyVideo | null): UploadVideoForm | null {
    if (video === null) return null;
    return {
        file: file,
    };
}

export function get_upload_status(file: UploadRawFile, video: AnyVideo | null, identifiers: Array<string>) {
    const decoder = new TextDecoder();
    if (video === null) return 'unsupported';
    if (video.level == 6) return 'custom';
    if (file.name.length >= 100) return 'filename';
    if (video.is_valid() == 1) return 'invalid';
    if (video.is_valid() == 3) return 'needApprove';
    if (!identifiers.includes(decoder.decode(video.player_identifier))) return 'identifier';
    return 'pass';
}

