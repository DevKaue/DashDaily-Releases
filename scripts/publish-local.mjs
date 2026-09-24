import { createHash } from "node:crypto";
import { createReadStream } from "node:fs";
import { access, stat } from "node:fs/promises";
import { basename, resolve } from "node:path";
import { spawnSync } from "node:child_process";

function argumentsMap(values) {
  const result = new Map();
  for (let index = 0; index < values.length; index += 2) {
    const key = values[index];
    const value = values[index + 1];
    if (!key?.startsWith("--") || value === undefined) throw new Error(`Argumento inválido: ${key}`);
    result.set(key.slice(2), value);
  }
  return result;
}

function required(map, key) {
  const value = map.get(key)?.trim();
  if (!value) throw new Error(`O argumento --${key} é obrigatório.`);
  return value;
}

function run(command, args) {
  const result = spawnSync(command, args, { cwd: repositoryRoot, encoding: "utf8", stdio: "inherit" });
  if (result.status !== 0) throw new Error(`Falha ao executar ${command} ${args[0] ?? ""}.`);
}

async function sha256(filePath) {
  const hash = createHash("sha256");
  for await (const chunk of createReadStream(filePath)) hash.update(chunk);
  return hash.digest("hex");
}

const repositoryRoot = resolve(import.meta.dirname, "..");
const args = argumentsMap(process.argv.slice(2));
const version = required(args, "version");
const versionCode = required(args, "version-code");
const apkPath = resolve(required(args, "apk"));
const notesPath = resolve(required(args, "notes"));
const mandatory = args.get("mandatory") === "true" ? "true" : "false";
const expectedApkName = `dashdaily-mobile-${version}-android.apk`;

if (basename(apkPath) !== expectedApkName) {
  throw new Error(`O APK precisa se chamar ${expectedApkName}.`);
}

await access(apkPath);
await access(notesPath);
const apkStat = await stat(apkPath);
const apkSha256 = await sha256(apkPath);

run(process.execPath, [
  "scripts/prepare-release.mjs",
  "--version",
  version,
  "--version-code",
  versionCode,
  "--notes",
  notesPath,
  "--sha256",
  apkSha256,
  "--size",
  String(apkStat.size),
  "--mandatory",
  mandatory,
  "--output",
  "releases",
]);
run(process.execPath, ["scripts/validate-catalog.mjs"]);
run("gh", [
  "release",
  "create",
  `v${version}`,
  apkPath,
  "--target",
  "main",
  "--title",
  `DashDaily Mobile ${version}`,
  "--notes-file",
  `releases/${version}.md`,
]);
run("git", ["add", "releases"]);
run("git", ["commit", "-m", `release: publica DashDaily Mobile ${version}`]);
run("git", ["push", "origin", "main"]);

console.log(`DashDaily Mobile ${version} publicado com SHA-256 ${apkSha256}.`);
