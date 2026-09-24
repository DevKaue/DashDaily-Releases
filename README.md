# DashDaily — Releases oficiais

Este repositório concentra os APKs oficiais do DashDaily, o catálogo consumido pelo atualizador do aplicativo e as notas de cada versão.

## Instalação

Baixe sempre o APK pela seção [Releases](https://github.com/DevKaue/DashDaily-Releases/releases). O aplicativo verifica automaticamente o arquivo `releases/latest.json`, apresenta as melhorias disponíveis, baixa o pacote e abre o instalador seguro do Android.

O Android exige uma confirmação antes de instalar ou substituir um APK. Essa confirmação não pode ser removida por aplicativos comuns distribuídos fora da Play Store.

## Estrutura

- `releases/latest.json`: catálogo da versão atual consumido pelo aplicativo.
- `releases/<versão>.md`: descrição completa das melhorias de cada versão.
- GitHub Releases: APKs assinados e checksums para validação.

## Publicação de uma nova versão

1. Gere e teste o APK no repositório principal.
2. Crie a release com a tag correspondente, por exemplo `v1.2.0`.
3. Anexe o APK e informe seu SHA-256.
4. Adicione as notas em `releases/1.2.0.md`.
5. Atualize `releases/latest.json` somente depois que o APK estiver disponível.

Nunca substitua o arquivo de uma versão existente. Publique uma nova versão para preservar rastreabilidade e permitir auditoria do checksum.
