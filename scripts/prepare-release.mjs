import { mkdir, readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

function readArguments(values) {
  const result = new Map();

  for (let index = 0; index < values.length; index += 2) {
    const key = values[index];
    const value = values[index + 1];

    if (!key?.startsWith("--") || value === undefined) {
      throw new Error(`Argumento inválido: ${key ?? "ausente"}`);
    }

    result.set(key.slice(2), value);
  }

  return result;
}

function required(argumentsMap, name) {
  const value = argumentsMap.get(name)?.trim();
  if (!value) throw new Error(`O argumento --${name} é obrigatório.`);
  return value;
}

function assertReleaseNotes(notes) {
  if (
    typeof notes !== "object" ||
    notes === null ||
    typeof notes.title !== "string" ||
    typeof notes.summary !== "string" ||
    !Array.isArray(notes.improvements) ||
    notes.improvements.length === 0 ||
    !notes.improvements.every((item) => typeof item === "string" && item.trim()) ||
    typeof notes.minimumVersion !== "string"
  ) {
    throw new Error("As notas da versão não possuem o formato esperado.");
  }
}

const argumentsMap = readArguments(process.argv.slice(2));
const version = required(argumentsMap, "version");
const versionCode = Number.parseInt(required(argumentsMap, "version-code"), 10);
const notesPath = resolve(required(argumentsMap, "notes"));
const sha256 = required(argumentsMap, "sha256").toLowerCase();
const sizeBytes = Number.parseInt(required(argumentsMap, "size"), 10);
const mandatory = required(argumentsMap, "mandatory") === "true";
const outputDirectory = resolve(required(argumentsMap, "output"));

if (!/^\d+\.\d+\.\d+$/.test(version)) throw new Error("A versão deve seguir o formato semântico X.Y.Z.");
if (!Number.isSafeInteger(versionCode) || versionCode < 1) throw new Error("Version code inválido.");
if (!/^[a-f0-9]{64}$/.test(sha256)) throw new Error("SHA-256 inválido.");
if (!Number.isSafeInteger(sizeBytes) || sizeBytes < 1) throw new Error("Tamanho do APK inválido.");

const notes = JSON.parse(await readFile(notesPath, "utf8"));
assertReleaseNotes(notes);

const publishedAt = new Date().toISOString();
const apkName = `dashdaily-mobile-${version}-android.apk`;
const downloadUrl = `https://github.com/DevKaue/DashDaily-Releases/releases/download/v${version}/${apkName}`;
const releaseNotesUrl = `https://github.com/DevKaue/DashDaily-Releases/blob/main/releases/${version}.md`;
const markdown = `# DashDaily Mobile ${version}

Publicada em ${publishedAt.slice(0, 10)}.

## ${notes.title}

${notes.summary}

## Melhorias

${notes.improvements.map((item) => `- ${item}`).join("\n")}

## APK Android

- Pacote: \`com.dashdaily.app\`
- Version code: \`${versionCode}\`
- SHA-256: \`${sha256}\`
- Tamanho: \`${sizeBytes}\` bytes

O APK desta versão está disponível nos anexos desta release.
`;
const catalog = {
  schemaVersion: 1,
  version,
  versionCode,
  minimumVersion: notes.minimumVersion,
  mandatory,
  publishedAt,
  title: notes.title,
  summary: notes.summary,
  improvements: notes.improvements,
  android: {
    packageName: "com.dashdaily.app",
    downloadUrl,
    sha256,
    sizeBytes,
  },
  releaseNotesUrl,
};

await mkdir(outputDirectory, { recursive: true });
await writeFile(resolve(outputDirectory, `${version}.md`), markdown, "utf8");
await writeFile(resolve(outputDirectory, "latest.json"), `${JSON.stringify(catalog, null, 2)}\n`, "utf8");

console.log(`Catálogo preparado para DashDaily ${version}.`);
