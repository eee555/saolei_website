import { UploadRawFile } from 'element-plus';
import JSZip from 'jszip';
import { AvfVideo, EvfVideo, MvfVideo, RmvVideo } from 'ms-toollib';

import { arbiterTimeStampToDate, generalTimeStampToDate } from './datetime';
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
        end_time: (video instanceof AvfVideo) ? arbiterTimeStampToDate(video.end_time) : generalTimeStampToDate(video.end_time),
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
    if (video === null) return 'fileext';
    if (video.level == 6) return 'custom';
    if (file.name.length >= 100) return 'filename';
    if (video.is_valid() == 1) return 'invalid';
    if (video.is_valid() == 3) return 'needApprove';
    if (!identifiers.includes(video.player_identifier)) return 'identifier';
    return 'pass';
}

export async function streamToZip(data: Uint8Array, filename: string) {
    const zip = new JSZip();
    let offset = 0;

    while (offset < data.length) {
        // Read 4-byte filename length
        const filenameLen = new DataView(data.buffer, offset, 4).getUint32(0, false);
        offset += 4;

        // Read filename
        const filenameBytes = data.slice(offset, offset + filenameLen);
        const filename = new TextDecoder().decode(filenameBytes);
        offset += filenameLen;

        // Read 8-byte file size
        const fileSize = Number(new DataView(data.buffer, offset, 8).getBigUint64(0, false));
        offset += 8;

        // Read file content
        const fileData = data.slice(offset, offset + fileSize);
        offset += fileSize;

        zip.file(filename, fileData);
    }

    const blob = await zip.generateAsync({ type: 'blob', compression: 'DEFLATE' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}
