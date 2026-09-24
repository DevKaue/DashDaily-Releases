# DashDaily — Releases oficiais

Este repositório concentra os APKs oficiais do DashDaily, o catálogo consumido pelo atualizador do aplicativo e as notas de cada versão.

## Instalação

Baixe sempre o APK pela seção [Releases](https://github.com/DevKaue/DashDaily-Releases/releases). O aplicativo verifica automaticamente o arquivo `releases/latest.json`, apresenta as melhorias disponíveis, baixa o pacote e abre o instalador seguro do Android.

O Android exige uma confirmação antes de instalar ou substituir um APK. Essa confirmação não pode ser removida por aplicativos comuns distribuídos fora da Play Store.

## Estrutura

- `releases/latest.json`: catálogo da versão atual consumido pelo aplicativo.
- `releases/<versão>.md`: descrição completa das melhorias de cada versão.
- `scripts/generate-guide.py`: gerador do guia oficial em PDF com dados da release atual.
- GitHub Releases: APKs assinados e checksums para validação.

## Publicação de uma nova versão

O build permanece no repositório privado do produto. O repositório público recebe somente o APK aprovado, as notas e o checksum — nunca o código-fonte ou uma credencial com acesso a ele.

Depois de gerar e testar o APK no projeto principal, execute o publicador local:

```bash
node scripts/publish-local.mjs \
  --version 1.2.0 \
  --version-code 4 \
  --apk /caminho/dashdaily-mobile-1.2.0-android.apk \
  --notes /caminho/1.2.0.json \
  --mandatory false
```

O comando calcula o SHA-256, gera as notas, cria a release imutável e, por último, publica o catálogo `latest.json`. O workflow deste repositório valida o catálogo a cada alteração.

Depois que o catálogo é atualizado, o workflow `Publicar guia em PDF` gera automaticamente um novo guia com a versão, melhorias, checksum e instruções atuais, valida suas 13 páginas e anexa o PDF à mesma release.

Nunca substitua o arquivo de uma versão existente. Publique uma nova versão para preservar rastreabilidade e permitir auditoria do checksum.
