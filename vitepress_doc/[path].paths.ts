import { getLocalizedPages } from './.vitepress/localized-pages';

export default {
    watch: ['zh/**/*.md', 'en/**/*.md'],
    paths() {
        const pages = getLocalizedPages();
        return [...new Set([...pages.zh, ...pages.en])].flatMap((page) => {
            const path = page.endsWith('/') ? `${page}index` : page;
            const aliases = page ? [path] : [];
            for (const locale of ['zh', 'en'] as const) {
                if (!pages[locale].includes(page)) aliases.push(`${locale}/${path}`);
            }
            return aliases.map((path) => ({ params: { path } }));
        });
    },
};
