import { UploadRawFile } from 'element-plus';
import { AvfVideo, EvfVideo, RmvVideo, MvfVideo } from 'ms-toollib';
import { VideoAbstract } from './videoabstract';
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
        video = new AvfVideo(stream, filename);
    } else if (ext === 'evf') {
        video = new EvfVideo(stream, filename);
    } else if (ext === 'rmv') {
        video = new RmvVideo(stream, filename);
    } else if (ext === 'mvf') {
        video = new MvfVideo(stream, filename);
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

export function extract_stat(video: AnyVideo | null): VideoAbstract | null {
    if (video === null) return null;
    video.current_time = 1e8;
    return new VideoAbstract({
        id: 0,
        level: ['b', 'i', 'e', 'c'][video.level - 3],
        mode: String(video.mode).padStart(2, '0'),
        software: get_software(video),
        timems: video.rtime_ms,
        bv: video.bbbv,
        ce: video.ce,
        cl: video.cl,
        end_time: new Date(Number(video.end_time / BigInt(1000))),
    });
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
    // const decoder = new TextDecoder();
    if (video === null) return 'unsupported';
    if (video.level == 6) return 'custom';
    if (file.name.length >= 100) return 'filename';
    if (video.is_valid() == 1) return 'invalid';
    if (video.is_valid() == 3) return 'needApprove';
    if (!identifiers.includes(video.player_identifier)) return 'identifier';
    return 'pass';
}

