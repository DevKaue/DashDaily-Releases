import { access, readFile } from "node:fs/promises";
import { resolve } from "node:path";

const repositoryRoot = resolve(import.meta.dirname, "..");
const catalogPath = resolve(repositoryRoot, "releases/latest.json");
const catalog = JSON.parse(await readFile(catalogPath, "utf8"));

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

assert(catalog.schemaVersion === 1, "schemaVersion deve ser 1.");
assert(/^\d+\.\d+\.\d+$/.test(catalog.version), "Versão semântica inválida.");
assert(Number.isSafeInteger(catalog.versionCode) && catalog.versionCode > 0, "Version code inválido.");
assert(typeof catalog.title === "string" && catalog.title.trim(), "Título ausente.");
assert(typeof catalog.summary === "string" && catalog.summary.trim(), "Resumo ausente.");
assert(Array.isArray(catalog.improvements) && catalog.improvements.length > 0, "Melhorias ausentes.");
assert(catalog.android?.packageName === "com.dashdaily.app", "Package name inválido.");
assert(/^[a-f0-9]{64}$/.test(catalog.android?.sha256), "SHA-256 inválido.");

const expectedDownloadUrl =
  `https://github.com/DevKaue/DashDaily-Releases/releases/download/v${catalog.version}/` +
  `dashdaily-mobile-${catalog.version}-android.apk`;
assert(catalog.android.downloadUrl === expectedDownloadUrl, "URL do APK não corresponde à versão publicada.");

const expectedNotesUrl =
  `https://github.com/DevKaue/DashDaily-Releases/blob/main/releases/${catalog.version}.md`;
assert(catalog.releaseNotesUrl === expectedNotesUrl, "URL das notas não corresponde à versão publicada.");
await access(resolve(repositoryRoot, `releases/${catalog.version}.md`));

console.log(`Catálogo DashDaily ${catalog.version} validado com sucesso.`);
