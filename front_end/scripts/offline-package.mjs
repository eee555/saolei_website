import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';

import JSZip from 'jszip';

export function validateInlineHtml(html) {
    if (/<script\b[^>]*\bsrc\s*=/iu.test(html) || /<link\b[^>]*\b(?:stylesheet|modulepreload)\b/iu.test(html)) throw new Error('HTML still loads external scripts or styles');
    const css = [...html.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/giu)].map((match) => match[1]).join('\n');
    const resourceUrls = [...css.matchAll(/url\(\s*["']?([^\s"')]+)/giu)].map((match) => match[1]);
    const externalResources = resourceUrls.filter((url) => !url.startsWith('data:') && !url.startsWith('#') && url !== 'about:blank');
    if (externalResources.length > 0) throw new Error(`External CSS resources: ${externalResources.join(', ')}`);
    return resourceUrls;
}

export async function writeBundledLicenses(output, dependencyLicenses) {
    if (dependencyLicenses.length === 0) throw new Error('Bundled dependency license list is empty');
    for (const entry of dependencyLicenses) {
        if (!entry.text) throw new Error(`Missing bundled license text: ${entry.name}@${entry.version}`);
    }
    await writeFile(join(output, 'THIRD_PARTY_LICENSES.json'), JSON.stringify(dependencyLicenses, null, 2));
    await writeFile(join(output, 'THIRD_PARTY_LICENSES.txt'), dependencyLicenses.map((entry) => `${entry.name}@${entry.version} (${entry.identifier ?? 'See notice'})\n${entry.source ? `Source: ${entry.source}\n` : ''}\n${entry.text}\n`).join('\n========================================\n\n'));
}

export async function writeOfflineArchive(frontend, output, packageName) {
    const zip = new JSZip();
    async function addDirectory(directory, prefix = '') {
        for (const entry of await readdir(directory, { withFileTypes: true })) {
            const filename = join(directory, entry.name);
            const archivePath = `${prefix}${entry.name}`;
            if (entry.isDirectory()) await addDirectory(filename, `${archivePath}/`);
            else zip.file(archivePath, await readFile(filename));
        }
    }
    await addDirectory(output);
    const zipPath = join(frontend, packageName);
    const zipData = await zip.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' });
    await writeFile(zipPath, zipData);
    const downloadPath = join(frontend, 'public', 'assets', packageName);
    await mkdir(dirname(downloadPath), { recursive: true });
    await writeFile(downloadPath, zipData);
    return { zipPath, downloadPath };
}
