export type LocalizedPages = Record<'zh' | 'en', string[]>;

export function getLocaleRedirect(url: URL, base: string, pages: LocalizedPages, browserLanguage: string): string | undefined {
    const basePath = base.replace(/\/$/, '');
    if (url.pathname !== basePath && !url.pathname.startsWith(`${basePath}/`)) return;
    const path = url.pathname.slice(basePath.length).replace(/^\//, '').replace(/\.html$/, '').replace(/(^|\/)index$/, '$1');
    const explicitLocale = /^(zh|en)(?:\/|$)/.exec(path)?.[1] as 'zh' | 'en' | undefined;
    if (explicitLocale) return;
    const requestedLanguage = url.searchParams.get('lang');
    const language = requestedLanguage === 'zh' || requestedLanguage === 'en' ? requestedLanguage : browserLanguage;
    const preferredLocale = language.toLowerCase().startsWith('zh') ? 'zh' : 'en';
    const page = path.replace(/\/$/, '');
    const availablePath = (locale: 'zh' | 'en') => pages[locale].find((entry) => entry.replace(/\/$/, '') === page);
    const preferredPath = availablePath(preferredLocale);
    const fallbackLocale = preferredLocale === 'zh' ? 'en' : 'zh';
    const targetPath = preferredPath ?? availablePath(fallbackLocale);
    if (targetPath === undefined) return;
    return `${basePath}/${preferredLocale}/${targetPath}${url.search}${url.hash}`;
}
