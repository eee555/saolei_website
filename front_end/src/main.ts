function markOutdatedBrowser() {
    document.documentElement.classList.add('outdated-browser');
}

function errorText(error: unknown) {
    if (typeof error === 'string') return error;
    if (typeof error !== 'object' || error === null || !('message' in error)) return '';

    const { message } = error;
    const stack = 'stack' in error ? error.stack : '';
    const messageText = typeof message === 'string' ? message : '';
    const stackText = typeof stack === 'string' ? stack : '';
    return `${messageText}\n${stackText}`;
}

function isSupportedBrowser() {
    return typeof Array.prototype.toReversed === 'function'
        && typeof Promise.withResolvers === 'function';
}

function isUnsupportedBrowserError(error: unknown) {
    const text = errorText(error);
    if (!text.includes('is not a function')) return false;
    return text.includes('toReversed') || text.includes('withResolvers');
}

// 站点依赖 Array.prototype.toReversed 与 Promise.withResolvers。
// 旧浏览器在启动时会抛出 `… is not a function`，页面会停在「1/3 正在加载资源」。
if (isSupportedBrowser()) {
    void import('./bootstrap').catch((error: unknown) => {
        if (isUnsupportedBrowserError(error)) markOutdatedBrowser();
        console.error(error);
    });
} else {
    markOutdatedBrowser();
}
