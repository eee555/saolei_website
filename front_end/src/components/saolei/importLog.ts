import { ArrayUtils } from '@/utils/arrays';
import { SaoleiVideo } from './utils';

type BaseLogTypes = 'videoStart' | 'videoSuccess' | 'videoError' | 'videoListStart' | 'videoListFinish' | 'videoListError' | 'pageEnd' | 'consoleError';

/**
 * 录像导入的基础日志类，用于记录各种元事件。
 *
 * 构造函数参数：
 * @param info
 * @param info.type BaseLogTypes
 * @param info.videoIndex 若有需要，记录录像索引
 * @param info.error 若有需要，记录错误信息
 *
 * 注意事项：
 * - 当type为'videoStart'、'videoSuccess'、'videoError'时，videoIndex会被记录
 * - 当type为'videoError'、'videoListError'、'consoleError'时，error会被记录
 */
class BaseLog {
    time: Date;
    type: BaseLogTypes;
    videoIndex?: number;
    error?: any;

    constructor(info: { type: BaseLogTypes; videoIndex?: number; error?: any }) {
        this.time = new Date(Date.now());
        this.type = info.type;
        if (['videoStart', 'videoSuccess', 'videoError'].includes(info.type)) {
            this.videoIndex = info.videoIndex;
        }
        if (['videoError', 'videoListError', 'consoleError'].includes(info.type)) {
            this.error = info.error;
        }
    }
}

/**
 * PageLog 类用于管理和记录页面级别的视频导入日志。该类跟踪视频列表的加载状态、当前导入的视频进度，并记录所有相关操作和错误。
 *
 * 主要功能：
 * - 管理视频列表的加载状态
 * - 跟踪视频导入进度
 * - 记录操作日志和错误信息
 *
 * 构造函数参数：
 * @param {number} index - 页面索引，用于标识当前页面的唯一编号
 *
 * 使用示例：
 *
 * 注意事项：
 * - 该类主要用于内部日志记录，不应直接用于业务逻辑处理
 * - 状态转换由内部方法自动管理，外部调用者不应直接修改 state 属性
 */
export class PageLog {
    public index: number;
    public videoLogs: BaseLog[] = [];
    public videoList: SaoleiVideo[] = [];
    public videoIndex: number = 0;
    public state: 'new' | 'normal' | 'end' | 'empty' = 'new';
    public hasError: boolean = false;

    constructor(index: number) {
        this.index = index;
    }

    /**
     * 获取正在导入的录像
     */
    public getVideo() {
        return this.videoList[this.videoIndex];
    }

    public pageEnd() {
        this.videoLogs.push({
            time: new Date(Date.now()),
            type: 'pageEnd',
        });
        this.state = 'end';
    }

    public isFinished() {
        return this.state === 'end' || this.state === 'empty';
    }

    /**
     * 开始加载本页录像列表
     */
    public videoListStart() {
        this.videoLogs.push(new BaseLog({
            type: 'videoListStart',
        }));
    }

    /**
     * 本页录像列表加载完成
     * @param {SaoleiVideo[]} list - 加载的录像列表
     */
    public videoListFinish(list: SaoleiVideo[]) {
        this.videoList = list;
        this.videoLogs.push({
            time: new Date(Date.now()),
            type: 'videoListFinish',
        });
        if (list.length === 0) {
            this.pageEnd();
        } else {
            this.state = 'normal';
        }
    }

    /**
     * 录像列表加载错误
     */
    public videoListError(object: string, category: string) {
        this.videoLogs.push({
            time: new Date(Date.now()),
            type: 'videoListError',
            error: {
                object: object,
                category: category,
            },
        });
        this.hasError = true;
        this.pageEnd();
    }

    /**
     * 开始导入当前录像
     */
    public VideoStart() {
        this.videoIndex++;
        if (this.videoIndex >= this.videoList.length) {
            this.videoLogs.push({
                time: new Date(Date.now()),
                type: 'pageEnd',
            });
            this.state = 'end';
            return;
        }
        this.videoLogs.push({
            time: new Date(Date.now()),
            type: 'videoStart',
            videoIndex: this.videoIndex,
        });
    }

    /**
     * 当前录像导入成功
     */
    public videoSuccess(video?: SaoleiVideo) {
        this.videoLogs.push({
            time: new Date(Date.now()),
            type: 'videoSuccess',
            videoIndex: this.videoIndex,
        });
        if (video !== undefined) {
            this.videoList[this.videoIndex] = video;
        }
    }

    /**
     * 当前录像导入报错
     */
    public videoError(object: string, category: string) {
        this.videoLogs.push({
            time: new Date(Date.now()),
            type: 'videoError',
            videoIndex: this.videoIndex,
            error: {
                object: object,
                category: category,
            },
        });
        this.hasError = true;
    }

    /**
     * 控制台错误
     */
    public consoleError(error: any) {
        this.videoLogs.push({
            time: new Date(Date.now()),
            type: 'consoleError',
            error: error,
        });
        this.hasError = true;
    }
}

export class ImportLog {
    public pageLogs: PageLog[] = [];
    public pageIndex: number = -1;
    public startWhen: Date = new Date(Date.now());
    public endWhen?: Date;

    public getCurrentPageLog() {
        return this.pageLogs[this.pageIndex];
    }
    public getCurrentVideo() {
        return this.getCurrentPageLog().getVideo();
    }

    public terminate() {
        this.endWhen = new Date(Date.now());
        this.getCurrentPageLog().pageEnd();
    }
    public isFinished() {
        return this.endWhen !== undefined;
    }

    public newPage(page: number | undefined = undefined) {
        if (page !== undefined) {
            this.pageLogs.push(new PageLog(page));
        } else {
            this.pageLogs.push(new PageLog(this.getCurrentPageLog().index + 1));
        }
        this.pageIndex += 1;
    }

    public videoListStart() {
        this.getCurrentPageLog().videoListStart();
    }
    public videoListFinish(list: SaoleiVideo[]) {
        this.getCurrentPageLog().videoListFinish(list);
    }
    public videoListError(object: string, category: string) {
        this.getCurrentPageLog().videoListError(object, category);
    }
    public videoListEmpty() {
        this.getCurrentPageLog().videoListFinish([]);
        this.getCurrentPageLog().state = 'empty';
        this.terminate();
    }

    public videoStart() {
        this.getCurrentPageLog().VideoStart();
    }
    public videoSuccess(video?: SaoleiVideo) {
        this.getCurrentPageLog().videoSuccess(video);
    }
    public videoError(object: string, category: string) {
        this.getCurrentPageLog().videoError(object, category);
    }

    public consoleError(error: any) {
        this.getCurrentPageLog().consoleError(error);
    }
}
