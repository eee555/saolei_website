import { ArrayUtils } from "./arrays";

/**
 * PiecewiseColorScheme 类用于根据给定的阈值和颜色数组，根据输入值返回相应的颜色。
 * 该类支持阈值数组按升序或降序排列，根据输入值返回对应的颜色。
 *
 * 核心功能：
 * - 根据输入值返回相应的颜色。
 * - 支持阈值数组按升序或降序排列。
 *
 * 使用示例：
 *
 * 构造函数参数：
 * - colors: string[] - 颜色数组，长度应与阈值数组长度加1。
 * - thresholds: number[] - 阈值数组，长度应与颜色数组长度减1。
 *
 * 使用限制：
 * - 颜色数组的长度应比阈值数组的长度多1。
 * - 阈值数组必须按升序或降序排列。
 * - 如果阈值数组既不是升序也不是降序，将抛出错误。
 *
 * 潜在副作用：
 * - 如果输入值不在阈值范围内，将返回最后一个颜色。
 */
export class PiecewiseColorScheme {
    private colors: string[];
    private thresholds: number[];
    private ascending: boolean;

    /**
     * 构造函数，初始化颜色和阈值数组，并检查阈值是否为升序或降序。
     * @param colors - 颜色数组
     * @param thresholds - 阈值数组
     */
    constructor(colors: string[], thresholds: number[]) {
        this.colors = colors;
        this.thresholds = thresholds;
        if (ArrayUtils.isAscending(thresholds)) {
            this.ascending = true;
        } else if (ArrayUtils.isDescending(thresholds)) {
            this.ascending = false;
        } else {
            throw new Error("Thresholds must be either ascending or descending");
        }
    }

    /**
     * 根据给定的值获取对应的颜色。
     *
     * @param value - 需要获取颜色的数值。
     * @returns 返回对应的颜色字符串。
     */
    public getColor(value: number): string {
        const index = ArrayUtils.getInsertIndex(this.thresholds, value, this.ascending);
        return this.colors[index];
    }
}
