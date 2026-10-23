/** 左右键按下、松开及移动事件，与具体游戏规则无关。 */
export type ClassicMouseEvent = 'lc' | 'lr' | 'rc' | 'rr' | 'mv';
export type ClassicMouseAction = 'left' | 'right' | 'chord';
export type ClassicMouseState = 'idle' | 'left-down' | 'right-down' | 'both-down' | 'chord-left-down' | 'chord-right-down';

interface Transition {
    readonly state: ClassicMouseState;
    readonly action?: ClassicMouseAction;
}

// 对应 vitepress_doc/zh/guide/minesweeper/mouse-event.md 的经典操作模式。
const transitions: Record<ClassicMouseState, Partial<Record<ClassicMouseEvent, Transition>>> = {
    idle: {
        lc: { state: 'left-down' },
        rc: { state: 'right-down', action: 'right' },
    },
    'left-down': {
        lr: { state: 'idle', action: 'left' },
        rc: { state: 'both-down' },
    },
    'right-down': {
        rr: { state: 'idle' },
        lc: { state: 'both-down' },
    },
    'both-down': {
        lr: { state: 'chord-right-down', action: 'chord' },
        rr: { state: 'chord-left-down', action: 'chord' },
    },
    'chord-left-down': {
        lr: { state: 'idle' },
        rc: { state: 'both-down' },
    },
    'chord-right-down': {
        rr: { state: 'idle' },
        lc: { state: 'both-down' },
    },
};

/**
 * 经典操作自动机：左键弹起、右键按下、双键首次弹起时产生操作意图。
 * 不读取棋盘、不执行游戏规则；调用方在触发事件的当前位置解释操作。
 */
export class ClassicMouseAutomaton {
    #state: ClassicMouseState = 'idle';

    public get state(): ClassicMouseState {
        return this.#state;
    }

    /** 无操作时返回 null；重复按下、未按下的松开和移动均不产生操作。 */
    public step(event: ClassicMouseEvent): ClassicMouseAction | null {
        const transition = transitions[this.#state][event];
        if (transition === undefined) return null;
        this.#state = transition.state;
        return transition.action ?? null;
    }

    /** 失焦、取消、重开或卸载时重置，不补发松开操作。 */
    public reset(): void {
        this.#state = 'idle';
    }
}
