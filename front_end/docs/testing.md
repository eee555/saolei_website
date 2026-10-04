# 测试文档

本文档说明项目内 Vitest、Cypress 组件测试和 Cypress e2e 测试的使用方式。

## 测试类型

项目目前有三类测试：

| 类型 | 文件位置 | 适用场景 |
| --- | --- | --- |
| Vitest | `src/**/*.test.ts` | 纯函数、数据转换、工具函数 |
| Cypress 组件测试 | `src/**/*.cy.ts`、`cypress/component/**/*.cy.ts` | Vue 组件及共享测试命令的行为 |
| Cypress e2e | `cypress/e2e/**/*.cy.ts` | 页面流程、路由跳转、登录注册、前后端联调 |

本文档仅提供基本的测试启动和目录结构。对于 Vitest 和 Cypress 的详细用法，请参照各自的官方文档。

## Vitest

运行全部 Vitest 测试：

```bash
npm run vitest
```

当前 Vitest 测试主要覆盖 `src/utils` 下的工具函数。新增纯函数或复杂数据转换逻辑时，优先补 `*.test.ts`。

建议：

- 测试文件与被测文件放在同目录。
- 命名为 `xxx.test.ts`。
- 优先测试输入输出和边界值，少依赖 DOM。
- 对日期时间、颜色、数组、表单校验等稳定逻辑补单元测试。

## Cypress 组件测试

组件测试文件通常与组件放在同目录，命名为 `*.cy.ts`。例如：

- `src/components/Footer.cy.ts`
- `src/components/VideoUpload/App.cy.ts`
- `src/components/visualization/ActivityCalendarAbstract/App.cy.ts`

打开 Cypress UI：

```bash
npx cypress open
```

运行 Cypress：

```bash
npx cypress run --component
```

组件测试由 Cypress 启动自己的 Vite dev server，不需要手动执行 `npm run dev`。

很多组件都依赖全局插件，这包括 `i18n`、`pinia` 和 `axios`，此时需要在 `cy.mount` 时传入额外参数。示例：

```ts
import Component from './Component.vue';

import $axios from '@/http';
import i18n from '@/i18n';
import { pinia } from '@/store/create';

cy.mount(Component, {
    global: {
        plugins: [i18n, pinia],
        config: {
            globalProperties: {
                $axios,
            },
        },
    },
});
```

组件测试的测试时区固定为 +8，测试语言固定为英文。

## Cypress e2e

e2e 测试位于 `cypress/e2e`。运行前需要启动后端和前端开发服务（详见各自的文档），然后运行：

```bash
npx cypress run --e2e
```

或打开 UI：

```bash
npx cypress open
```

e2e 测试的测试时区固定为 +8，测试语言固定为中文。

## 共享 Cypress 命令

组件测试和 e2e 均加载 `cypress/support/commands.ts`。验证弹窗、浮层或加载遮罩已关闭时，如果允许它被移除或保留为隐藏节点，使用：

```ts
cy.shouldBeAbsentOrHidden('.el-dialog');
cy.shouldBeAbsentOrHidden('.el-loading-mask', { timeout: 10000 });
```

该命令在当前文档中重新查询 CSS 选择器，直到没有匹配元素，或全部匹配元素都被 Cypress 判定为不可见。支持默认命令超时及显式 `timeout`，组件关闭动画期间会自动重试。调用前应先确认浮层已打开或加载已开始，避免初始未出现就满足关闭断言。

需要验证 DOM 确实被移除时，仍使用 `should('not.exist')`；需要验证节点保留但隐藏时，使用 `should('not.be.visible')`。

共享命令的回归测试位于 `cypress/component/commands.cy.ts`。

## 选择测试类型

新增测试时，为了提高测试性能，能用 Vitest 就用 Vitest，能不用 e2e 就不用 e2e。所以一般来说会有如下的分类：

1. Vitest：纯 TypeScript 工具类/工具函数。
2. Cypress 组件测试：方便模拟 props 和 request 的 Vue 组件。
3. Cypress e2e：多页面流程、路由、真实后端联调。

## 常用命令

```bash
npm run vitest
npx cypress open
npx cypress run --component
npx cypress run --e2e
```
