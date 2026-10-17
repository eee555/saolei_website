export function getDocsUrl(path: string, language: string): string {
    if (import.meta.env.VITE_OFFLINE_ANALYZER === 'true') return `${language.toLowerCase().startsWith('zh') ? 'help' : 'help/en'}/${path}.html`;
    const base = typeof import.meta.env.VITE_DOCS_URL === 'string' && import.meta.env.VITE_DOCS_URL.length > 0
        ? import.meta.env.VITE_DOCS_URL
        : import.meta.env.DEV ? 'http://localhost:5173/docs/' : '/docs/';
    const normalizedBase = base.endsWith('/') ? base : `${base}/`;
    const prefix = language.toLowerCase().startsWith('zh') ? '' : 'en/';
    const url = `${normalizedBase}${prefix}${path}`;
    return path ? url : `${url}?lang=${prefix ? 'en' : 'zh'}`;
}
