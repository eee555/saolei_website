# 测试文档

本文档说明项目内 Vitest、Cypress 组件测试和 Cypress e2e 测试的使用方式。

## 测试类型

项目目前有三类测试：

| 类型 | 文件位置 | 适用场景 |
| --- | --- | --- |
| Vitest | `src/**/*.test.ts` | 纯函数、数据转换、工具函数 |
| Cypress 组件测试 | `src/**/*.cy.ts` | 单个 Vue 组件的渲染、交互、边界状态 |
| Cypress e2e | `cypress/e2e/**/*.cy.ts` | 页面流程、路由跳转、登录注册、前后端联调 |

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

组件测试不需要手动启动 `npm run dev`。Cypress 会根据 [cypress.config.ts](../cypress.config.ts) 中的配置启动 Vite dev server：

```ts
component: {
    devServer: {
        framework: 'vue',
        bundler: 'vite',
    },
}
```

如果组件依赖全局插件，需要在 `cy.mount` 时传入 `global.plugins` 或 `global.config.globalProperties`。例如组件依赖 i18n 和 `$axios` 时：

```ts
import Component from './Component.vue';

import $axios from '@/http';
import i18n from '@/i18n';

cy.mount(Component, {
    global: {
        plugins: [i18n],
        config: {
            globalProperties: {
                $axios,
            },
        },
    },
});
```

组件测试的全局支持文件是 [cypress/support/component.ts](../cypress/support/component.ts)，其中注册了 `cy.mount`，并把测试时区固定为 `Asia/Shanghai`。

## Cypress e2e

e2e 测试位于 `cypress/e2e`。运行前需要启动前端开发服务：

```bash
npm run dev
```

然后运行：

```bash
npx cypress run --e2e
```

或打开 UI：

```bash
npx cypress open
```

e2e 的 `baseUrl` 是 `http://localhost:8080`。涉及真实账号、数据库或后端接口的用例，还需要启动本地后端服务，默认接口地址是 `http://127.0.0.1:8000`。

[cypress/support/e2e.ts](../cypress/support/e2e.ts) 提供了若干自定义命令：

- `cy.register(...)`
- `cy.setStaff(...)`
- `cy.login(...)`
- `cy.deleteUser()`
- `cy.flushDatabase()`
- `cy.visitUser(...)`

这些命令会请求本地后端的 dangerzone 接口。运行相关 e2e 前，请确认后端处于测试可用状态，避免误连线上服务。

## Mock 与 fixtures

通用 Cypress 命令位于 [cypress/support/commands.ts](../cypress/support/commands.ts)，包含：

- `cy.mockCaptchaRefresh(...)`
- `cy.mockGetEmailCode(...)`
- `cy.mockLogin()`
- `cy.mockRegister()`
- `cy.getLocalStorage(...)`
- `cy.setLocalStorage(...)`
- `cy.closeElNotifications()`
- `cy.extractTableData()`

测试数据文件放在 `cypress/fixtures`。涉及上传、解析录像或接口返回数据时，优先复用 fixture，避免在测试内写大段静态数据。

## 选择测试类型

新增测试时可以按这个顺序判断：

1. 纯函数或数据转换：写 Vitest。
2. 单个组件交互或渲染状态：写 Cypress 组件测试。
3. 多页面流程、路由、登录状态、真实后端联调：写 Cypress e2e。

如果一个页面很难做组件测试，可以先用 e2e 覆盖主路径，再把可拆出的纯逻辑补 Vitest。

## 写测试的约定

- 优先断言用户可见结果，而不是内部实现细节。
- 需要定位测试元素时使用 `data-cy`；生产构建会移除 Vue 文件中的 `data-cy` 属性。
- 避免依赖不稳定的等待时间，优先等待请求别名、元素状态或 URL。
- 涉及语言文本时，注意 Cypress e2e 默认 Chrome 启动参数包含 `--accept-lang=zh-CN`。
- 对会改变数据库状态的 e2e，用例开始前清理或准备数据。

## 常用命令

```bash
npm run vitest
npx cypress open
npx cypress run --component
npx cypress run --e2e
```

提交前建议至少运行与改动相关的测试；改动通用工具、上传、登录、用户资料、可视化组件时，优先补充或运行相邻测试。
