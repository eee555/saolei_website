import { defineConfig } from 'vitepress';
import type MarkdownIt from 'markdown-it';
import { graphvizMarkdownPlugin } from 'vitepress-plugin-graphviz';

const mainSiteLink = process.env.VITEPRESS_MAIN_SITE_URL
    ?? (process.env.NODE_ENV === 'development' ? 'http://localhost:8080/' : 'https://openms.top/');

async function configureDiagramFences(md: MarkdownIt) {
    const defaultFence = md.renderer.rules.fence;

    md.renderer.rules.fence = (tokens, idx, options, env, self) => {
        const token = tokens[idx];
        const info = token.info.trim().split(/\s+/)[0];

        if (info === 'automaton' || info === 'mermaid') {
            return `<MermaidDiagram encoded-source="${encodeURIComponent(token.content)}" />`;
        }

        return defaultFence
            ? defaultFence(tokens, idx, options, env, self)
            : self.renderToken(tokens, idx, options);
    };

    await graphvizMarkdownPlugin(md, {
        processors: {
            neato: {
                preprocess: (content) => content,
            },
        },
    });
}

export default defineConfig({
    title: '开源扫雷网使用指南',
    description: '开源扫雷网用户指南',
    base: process.env.VITEPRESS_BASE ?? '/docs/',
    cleanUrls: true,
    lastUpdated: true,
    sitemap: {
        hostname: 'https://openms.top',
        outFilename: 'sitemap.xml',
    },
    head: [
        ['meta', { property: 'og:type', content: 'website' }],
        ['meta', { property: 'og:site_name', content: '开源扫雷网' }],
        ['meta', { property: 'og:url', content: 'https://openms.top/docs/' }],
        ['meta', { name: 'robots', content: 'index, follow' }],
        ['link', { rel: 'canonical', href: 'https://openms.top/docs/' }],
    ],
    markdown: {
        config: configureDiagramFences,
    },
    locales: {
        root: {
            label: '简体中文',
            lang: 'zh-CN',
            title: '开源扫雷网使用指南',
            description: '开源扫雷网用户指南',
            themeConfig: {
                editLink: {
                    pattern: 'https://github.com/eee555/saolei_website/edit/main/vitepress_doc/:path',
                    text: '编辑本页',
                },
                footer: {
                    copyright: '版权所有 @ 2023-2026 开源扫雷网 openms.top',
                },
                lastUpdated: {
                    text: '最后更新',
                    formatOptions: {
                        dateStyle: 'medium',
                        timeStyle: 'short',
                        forceLocale: true,
                    },
                },
                nav: [
                    { text: '返回主站', link: mainSiteLink, target: '_self', rel: '' },
                ],
                sidebar: {
                    '/': [
                        {
                            text: '使用指南',
                            items: [
                                { text: '账号关联', link: '/guide/account-links' },
                                { text: '扫雷软件', link: '/guide/software' },
                                { text: '录像播放器', link: '/guide/video-player' },
                                { text: '扫雷标识', link: '/guide/identifier' },
                                {
                                    text: '比赛功能',
                                    link: '/guide/tournament',
                                    items: [
                                        { text: '金羊杯', link: '/guide/gsc' },
                                        { text: '打卡赛', link: '/guide/weekly-tournament' },
                                    ],
                                },
                                { text: '参与贡献', link: '/guide/contribute' },
                                { text: '网站收支', link: '/guide/balance' },
                            ],
                        },
                        {
                            text: '扫雷教程',
                            items: [
                                { text: '操作方式和规则', link: '/guide/minesweeper/mouse-event' },
                                { text: '术语', link: '/guide/minesweeper/terminology' },
                                { text: '数据', link: '/guide/minesweeper/stat' },
                            ],
                        },
                        {
                            text: '开发文档',
                            items: [
                                { text: '信号触发关系', link: '/guide/development/signals' },
                                { text: '缓存结构', link: '/guide/development/cache' },
                            ],
                        },
                    ],
                },
            },
        },
        en: {
            label: 'English',
            lang: 'en-US',
            title: 'Open Minesweeper Guide',
            description: 'Open Minesweeper user guide',
            themeConfig: {
                editLink: {
                    pattern: 'https://github.com/eee555/saolei_website/edit/main/vitepress_doc/:path',
                },
                footer: {
                    copyright: 'Copyright @ 2023-2026 Open Minesweeper openms.top',
                },
                lastUpdated: {
                    text: 'Last updated',
                    formatOptions: {
                        dateStyle: 'medium',
                        timeStyle: 'short',
                        forceLocale: true,
                    },
                },
                nav: [
                    { text: 'Main Site', link: mainSiteLink, target: '_self', rel: '' },
                ],
                sidebar: {
                    '/en/': [
                        {
                            text: 'User Guide',
                            items: [
                                { text: 'Account Links', link: '/en/guide/account-links' },
                                { text: 'Minesweeper Software', link: '/en/guide/software' },
                                { text: 'Video Player', link: '/en/guide/video-player' },
                                { text: 'Player Identifiers', link: '/en/guide/identifier' },
                                {
                                    text: 'Tournaments',
                                    link: '/en/guide/tournament',
                                    items: [
                                        { text: 'Golden Sheep Cup', link: '/en/guide/gsc' },
                                        { text: 'Weekly Tournament', link: '/en/guide/weekly-tournament' },
                                    ],
                                },
                                { text: 'Contributing', link: '/en/guide/contribute' },
                                { text: 'Website Finances', link: '/en/guide/balance' },
                            ],
                        },
                        {
                            text: 'Minesweeper Tutorials',
                            items: [
                                { text: 'Controls and Rules', link: '/en/guide/minesweeper/mouse-event' },
                                { text: 'Terminology', link: '/en/guide/minesweeper/terminology' },
                            ],
                        },
                    ],
                },
            },
        },
    },
    themeConfig: {
        logo: '/logo.png',
        search: {
            provider: 'local',
        },
        socialLinks: [
            { icon: 'github', link: 'https://github.com/eee555/saolei_website' },
            { icon: 'gitee', link: 'https://gitee.com/ee55/saolei_website' },
            { icon: 'discord', link: 'https://discord.gg/ks8ngPX5bT' },
            { icon: 'qq', link: 'https://qm.qq.com/q/hNShGUQkJG' },
        ],
    },
});
