# Segurança do canal de atualização

Os APKs oficiais do DashDaily são publicados exclusivamente nas releases deste repositório e assinados por uma chave Android persistente, armazenada como segredo criptografado do GitHub Actions.

O aplicativo aceita catálogos e downloads apenas por HTTPS e valida se o APK pertence ao caminho oficial `DevKaue/DashDaily-Releases`. Durante a instalação, o Android também confere se a assinatura do novo pacote corresponde à assinatura do aplicativo instalado.

Os checksums SHA-256 ficam registrados nas notas e no catálogo de cada versão. Releases já publicadas não devem ser sobrescritas.

## Limitação da instalação

Aplicativos distribuídos fora da Play Store não podem se reinstalar silenciosamente. O DashDaily baixa a atualização e abre o instalador, mas a confirmação final permanece sob controle do usuário e do Android.
