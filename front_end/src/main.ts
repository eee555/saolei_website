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

function isToReversedError(error: unknown) {
    const text = errorText(error);
    return text.includes('toReversed') && text.includes('is not a function');
}

// 旧浏览器没有 Array.prototype.toReversed。store 在求值时会抛出
// `toReversed is not a function`，启动页就会停在「1/3 正在加载资源」。
if (typeof Array.prototype.toReversed === 'function') {
    void import('./bootstrap').catch((error: unknown) => {
        if (isToReversedError(error)) markOutdatedBrowser();
        console.error(error);
    });
} else {
    markOutdatedBrowser();
}
