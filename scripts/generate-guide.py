#!/usr/bin/env python3
"""Generate the official DashDaily user guide from the public release catalog."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle


PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_X = 20 * mm
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN_X

INK = colors.HexColor("#13231D")
MUTED = colors.HexColor("#617068")
SUBTLE = colors.HexColor("#87938C")
GREEN = colors.HexColor("#15805F")
GREEN_DARK = colors.HexColor("#0B4F3B")
GREEN_SOFT = colors.HexColor("#E9F6F0")
BLUE = colors.HexColor("#2F6FEB")
BLUE_SOFT = colors.HexColor("#EBF2FF")
AMBER = colors.HexColor("#A86512")
AMBER_SOFT = colors.HexColor("#FFF4E1")
RED = colors.HexColor("#B33A32")
RED_SOFT = colors.HexColor("#FCEDEA")
PAPER = colors.HexColor("#F7F9F6")
WHITE = colors.white
BORDER = colors.HexColor("#DCE5DF")


def register_fonts() -> None:
    regular = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    bold = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    mono = Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("DashSans", str(regular)))
        pdfmetrics.registerFont(TTFont("DashSans-Bold", str(bold)))
        if mono.exists():
            pdfmetrics.registerFont(TTFont("DashMono", str(mono)))
        else:
            pdfmetrics.registerFont(TTFont("DashMono", str(regular)))
    else:
        pdfmetrics.registerFont(TTFont("DashSans", str(regular)))


register_fonts()

BODY = ParagraphStyle(
    "Body",
    fontName="DashSans",
    fontSize=9.2,
    leading=14,
    textColor=INK,
    spaceAfter=0,
)
SMALL = ParagraphStyle(
    "Small",
    parent=BODY,
    fontSize=7.8,
    leading=11,
    textColor=MUTED,
)
MUTED_BODY = ParagraphStyle(
    "MutedBody",
    parent=BODY,
    textColor=MUTED,
)
CARD_TITLE = ParagraphStyle(
    "CardTitle",
    parent=BODY,
    fontName="DashSans-Bold",
    fontSize=9.5,
    leading=13,
    textColor=INK,
)
TITLE = ParagraphStyle(
    "Title",
    fontName="DashSans-Bold",
    fontSize=23,
    leading=28,
    textColor=INK,
)
SUBTITLE = ParagraphStyle(
    "Subtitle",
    fontName="DashSans",
    fontSize=11,
    leading=16,
    textColor=MUTED,
)
MONO = ParagraphStyle(
    "Mono",
    fontName="DashMono",
    fontSize=7,
    leading=10,
    textColor=INK,
    wordWrap="CJK",
)


def pt(value: float) -> float:
    return value * mm


def draw_paragraph(
    pdf: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width: float,
    style: ParagraphStyle = BODY,
) -> float:
    paragraph = Paragraph(text, style)
    _, height = paragraph.wrap(width, PAGE_HEIGHT)
    paragraph.drawOn(pdf, x, y - height)
    return y - height


def draw_footer(pdf: canvas.Canvas, version: str, page_number: int) -> None:
    pdf.setStrokeColor(BORDER)
    pdf.setLineWidth(0.5)
    pdf.line(MARGIN_X, pt(16), PAGE_WIDTH - MARGIN_X, pt(16))
    pdf.setFont("DashSans", 7.2)
    pdf.setFillColor(SUBTLE)
    pdf.drawString(MARGIN_X, pt(10), f"Guia de utilização - versão {version}")
    pdf.drawRightString(PAGE_WIDTH - MARGIN_X, pt(10), f"{page_number:02d}")


def draw_header(pdf: canvas.Canvas, label: str, section_number: str, version: str, page_number: int) -> float:
    pdf.setFillColor(INK)
    pdf.setFont("DashSans-Bold", 8)
    pdf.drawString(MARGIN_X, PAGE_HEIGHT - pt(15), "DASHDAILY")
    pdf.setFillColor(GREEN)
    pdf.drawRightString(PAGE_WIDTH - MARGIN_X, PAGE_HEIGHT - pt(15), f"{section_number}  /  {label.upper()}")
    draw_footer(pdf, version, page_number)
    return PAGE_HEIGHT - pt(30)


def draw_title(pdf: canvas.Canvas, title: str, subtitle: str, y: float) -> float:
    y = draw_paragraph(pdf, title, MARGIN_X, y, CONTENT_WIDTH, TITLE)
    y -= pt(3)
    y = draw_paragraph(pdf, subtitle, MARGIN_X, y, CONTENT_WIDTH, SUBTITLE)
    return y - pt(8)


def draw_step(pdf: canvas.Canvas, number: int, title: str, text: str, y: float) -> float:
    pdf.setFillColor(GREEN)
    pdf.circle(MARGIN_X + pt(4), y - pt(4), pt(4), fill=1, stroke=0)
    pdf.setFillColor(WHITE)
    pdf.setFont("DashSans-Bold", 7.2)
    pdf.drawCentredString(MARGIN_X + pt(4), y - pt(5.3), f"{number:02d}")
    text_x = MARGIN_X + pt(13)
    y_title = draw_paragraph(pdf, title, text_x, y, CONTENT_WIDTH - pt(13), CARD_TITLE)
    y_text = draw_paragraph(pdf, text, text_x, y_title - pt(1), CONTENT_WIDTH - pt(13), MUTED_BODY)
    return y_text - pt(5)


def draw_bullet(pdf: canvas.Canvas, text: str, y: float, color: colors.Color = GREEN) -> float:
    pdf.setFillColor(color)
    pdf.circle(MARGIN_X + pt(2), y - pt(2.6), pt(1.25), fill=1, stroke=0)
    return draw_paragraph(pdf, text, MARGIN_X + pt(7), y, CONTENT_WIDTH - pt(7), MUTED_BODY) - pt(3)


def draw_callout(
    pdf: canvas.Canvas,
    title: str,
    text: str,
    y: float,
    background: colors.Color = GREEN_SOFT,
    accent: colors.Color = GREEN,
    height: float = pt(32),
) -> float:
    pdf.setFillColor(background)
    pdf.roundRect(MARGIN_X, y - height, CONTENT_WIDTH, height, pt(4), fill=1, stroke=0)
    pdf.setFillColor(accent)
    pdf.roundRect(MARGIN_X, y - height, pt(2), height, pt(1), fill=1, stroke=0)
    text_x = MARGIN_X + pt(8)
    title_y = draw_paragraph(pdf, title, text_x, y - pt(6), CONTENT_WIDTH - pt(14), CARD_TITLE)
    draw_paragraph(pdf, text, text_x, title_y - pt(2), CONTENT_WIDTH - pt(14), SMALL)
    return y - height - pt(7)


def draw_two_cards(pdf: canvas.Canvas, cards: list[tuple[str, str]], y: float, height: float = pt(34)) -> float:
    gap = pt(5)
    width = (CONTENT_WIDTH - gap) / 2
    for index, (title, text) in enumerate(cards):
        x = MARGIN_X + index * (width + gap)
        pdf.setFillColor(WHITE)
        pdf.setStrokeColor(BORDER)
        pdf.roundRect(x, y - height, width, height, pt(4), fill=1, stroke=1)
        title_y = draw_paragraph(pdf, title, x + pt(6), y - pt(6), width - pt(12), CARD_TITLE)
        draw_paragraph(pdf, text, x + pt(6), title_y - pt(2), width - pt(12), SMALL)
    return y - height - pt(7)


def draw_simple_table(pdf: canvas.Canvas, rows: list[list[str]], y: float, widths: list[float]) -> float:
    data = [[Paragraph(cell, CARD_TITLE if row_index == 0 else SMALL) for cell in row] for row_index, row in enumerate(rows)]
    table = Table(data, colWidths=widths, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), GREEN_SOFT),
                ("TEXTCOLOR", (0, 0), (-1, 0), GREEN_DARK),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    _, height = table.wrap(CONTENT_WIDTH, PAGE_HEIGHT)
    table.drawOn(pdf, MARGIN_X, y - height)
    return y - height - pt(6)


def next_page(pdf: canvas.Canvas) -> None:
    pdf.showPage()
    pdf.setFillColor(PAPER)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)


def format_date(value: str) -> str:
    months = [
        "janeiro",
        "fevereiro",
        "março",
        "abril",
        "maio",
        "junho",
        "julho",
        "agosto",
        "setembro",
        "outubro",
        "novembro",
        "dezembro",
    ]
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return f"{parsed.day} de {months[parsed.month - 1]} de {parsed.year}"


def build_guide(catalog: dict, output_path: Path) -> None:
    version = catalog["version"]
    version_code = catalog["versionCode"]
    published_at = format_date(catalog["publishedAt"])
    android = catalog["android"]
    page_count = 13

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output_path), pagesize=A4, pageCompression=1)
    pdf.setTitle(f"Guia de Utilização DashDaily {version}")
    pdf.setAuthor("DashDaily")
    pdf.setSubject("Guia oficial do usuário Web e Android, incluindo atualizações integradas")
    pdf.setKeywords("DashDaily, guia, finanças, Android, atualização, segurança")

    # Cover
    pdf.setFillColor(GREEN_DARK)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    pdf.setFillColor(colors.HexColor("#1A9470"))
    pdf.circle(PAGE_WIDTH + pt(5), PAGE_HEIGHT - pt(25), pt(72), fill=1, stroke=0)
    pdf.setFillColor(colors.HexColor("#0D5F47"))
    pdf.circle(-pt(8), pt(18), pt(65), fill=1, stroke=0)
    pdf.setFillColor(WHITE)
    pdf.roundRect(MARGIN_X, PAGE_HEIGHT - pt(45), pt(24), pt(24), pt(5), fill=1, stroke=0)
    pdf.setFillColor(GREEN_DARK)
    pdf.setFont("DashSans-Bold", 15)
    pdf.drawCentredString(MARGIN_X + pt(12), PAGE_HEIGHT - pt(31), "DD")
    pdf.setFillColor(colors.HexColor("#A7F3D0"))
    pdf.setFont("DashSans-Bold", 8)
    pdf.drawString(MARGIN_X, PAGE_HEIGHT - pt(60), f"GUIA OFICIAL  /  {version}")
    cover_title = ParagraphStyle("CoverTitle", parent=TITLE, fontSize=31, leading=37, textColor=WHITE)
    cover_subtitle = ParagraphStyle("CoverSubtitle", parent=SUBTITLE, fontSize=12, leading=18, textColor=colors.HexColor("#D6EAE2"))
    y = PAGE_HEIGHT - pt(88)
    y = draw_paragraph(pdf, "Controle sua vida<br/>financeira com clareza.", MARGIN_X, y, pt(140), cover_title)
    y -= pt(8)
    draw_paragraph(
        pdf,
        "Guia completo para usar o DashDaily na Web e no Android, incluindo instalação segura e atualizações integradas.",
        MARGIN_X,
        y,
        pt(140),
        cover_subtitle,
    )
    pdf.setFillColor(colors.HexColor("#A7F3D0"))
    pdf.roundRect(MARGIN_X, pt(53), pt(121), pt(12), pt(6), fill=1, stroke=0)
    pdf.setFillColor(GREEN_DARK)
    pdf.setFont("DashSans-Bold", 7.6)
    pdf.drawCentredString(MARGIN_X + pt(60.5), pt(57), "WEB  /  ANDROID  /  SEGURANÇA  /  SUPORTE")
    pdf.setFillColor(colors.HexColor("#D6EAE2"))
    pdf.setFont("DashSans", 8)
    pdf.drawString(MARGIN_X, pt(35), f"Atualizado em {published_at}")
    pdf.drawRightString(PAGE_WIDTH - MARGIN_X, pt(35), f"{page_count} páginas")

    # Contents
    next_page(pdf)
    y = draw_header(pdf, "Comece aqui", "00", version, 2)
    y = draw_title(pdf, "Seu mapa do DashDaily", "A jornada mais curta para configurar a conta e transformar registros em decisões úteis.", y)
    contents = [
        ("01", "Primeiro acesso e segurança", "03"),
        ("02", "Dashboard e leitura dos números", "04"),
        ("03", "Transações, orçamento e categorias", "05"),
        ("04", "Cartões, investimentos e metas", "06"),
        ("05", "Relatórios, insights e notificações", "07"),
        ("06", "Espaços compartilhados e assinatura", "08"),
        ("07", "Preferências, perfil e privacidade", "09"),
        ("08", "Instalação segura no Android", "10"),
        ("09", "Atualizações integradas", "11"),
        ("10", "Solução de problemas", "12"),
        ("11", "Novidades da versão", "13"),
    ]
    for number, label, page in contents:
        pdf.setFillColor(GREEN_SOFT)
        pdf.circle(MARGIN_X + pt(5), y - pt(3), pt(5), fill=1, stroke=0)
        pdf.setFillColor(GREEN_DARK)
        pdf.setFont("DashSans-Bold", 7)
        pdf.drawCentredString(MARGIN_X + pt(5), y - pt(4.2), number)
        pdf.setFillColor(INK)
        pdf.setFont("DashSans-Bold", 9.2)
        pdf.drawString(MARGIN_X + pt(15), y - pt(4.1), label)
        pdf.setStrokeColor(BORDER)
        pdf.setDash(1, 2)
        pdf.line(MARGIN_X + pt(90), y - pt(3.5), PAGE_WIDTH - MARGIN_X - pt(10), y - pt(3.5))
        pdf.setDash()
        pdf.setFillColor(MUTED)
        pdf.drawRightString(PAGE_WIDTH - MARGIN_X, y - pt(4.1), page)
        y -= pt(13.4)
    draw_callout(
        pdf,
        "Comece pela Web",
        "Acesse dashdaily-web.vercel.app, crie a conta e conclua o onboarding. Depois use as mesmas credenciais no Android.",
        y - pt(2),
        BLUE_SOFT,
        BLUE,
    )

    # Access
    next_page(pdf)
    y = draw_header(pdf, "Acesso", "01", version, 3)
    y = draw_title(pdf, "Primeiro acesso e segurança", "Crie a conta, recupere a senha e entenda como a sessão é protegida.", y)
    y = draw_step(pdf, 1, "Criar a conta", "Na tela de login, escolha Criar conta grátis. Informe nome, e-mail válido e uma senha com pelo menos 8 caracteres.", y)
    y = draw_step(pdf, 2, "Concluir o onboarding", "Defina moeda, idioma e preferências iniciais para personalizar valores, alertas e o painel.", y)
    y = draw_step(pdf, 3, "Entrar novamente", "Na Web, a renovação usa cookie HttpOnly. No Android, as credenciais ficam no armazenamento seguro do aparelho.", y)
    y = draw_two_cards(pdf, [
        ("Esqueci minha senha", "Solicite um link pelo e-mail cadastrado. O link expira e só pode ser usado uma vez."),
        ("Trocar senha", "Abra Perfil, informe a senha atual e escolha uma nova senha exclusiva."),
    ], y)
    y = draw_callout(pdf, "Boa prática", "O DashDaily nunca pede sua senha por mensagem. Links de recuperação devem apontar para os domínios oficiais.", y)
    y = draw_paragraph(pdf, "O que visitantes podem acessar", MARGIN_X, y, CONTENT_WIDTH, CARD_TITLE) - pt(4)
    y = draw_bullet(pdf, "Página inicial, login, cadastro e recuperação de senha.", y)
    y = draw_bullet(pdf, "Endpoint técnico de saúde e webhook do provedor, protegido por assinatura.", y)
    draw_bullet(pdf, "Nenhum dashboard, perfil, transação, relatório ou preferência sem sessão válida.", y)

    # Dashboard
    next_page(pdf)
    y = draw_header(pdf, "Visão geral", "02", version, 4)
    y = draw_title(
        pdf,
        "Entenda o dashboard",
        "Use o painel como fotografia do período. No celular, navegue por Início, Transações, Orçamento, Metas e Mais.",
        y,
    )
    y = draw_two_cards(pdf, [
        ("Saldo", "Receitas menos despesas no período. Resultado negativo exige revisão."),
        ("Receitas", "Total de salário, renda extra, reembolsos e outras entradas."),
    ], y)
    y = draw_two_cards(pdf, [
        ("Despesas", "Total de saídas. Observe concentração por categoria e recorrência."),
        ("Investido", "Valor atual consolidado dos investimentos cadastrados."),
    ], y)
    y = draw_paragraph(pdf, "Como ler sem se perder", MARGIN_X, y, CONTENT_WIDTH, CARD_TITLE) - pt(4)
    y = draw_step(pdf, 1, "Confira o período", "Valide mês, ano ou intervalo antes de comparar números.", y)
    y = draw_step(pdf, 2, "Observe a tendência", "Receitas versus despesas mostra direção, não apenas um valor isolado.", y)
    y = draw_step(pdf, 3, "Localize a causa", "Use categorias e transações recentes para entender o resultado.", y)
    y = draw_step(pdf, 4, "Transforme em ação", "Ajuste uma despesa, defina uma meta ou revise o orçamento.", y)
    draw_callout(pdf, "Dashboard vazio?", "Cadastre uma receita e uma despesa. Depois volte ao início para visualizar indicadores calculados com seus dados.", y)

    # Transactions
    next_page(pdf)
    y = draw_header(pdf, "Rotina", "03", version, 5)
    y = draw_title(pdf, "Transações e orçamento", "Uma rotina simples de registro produz relatórios melhores e decisões mais seguras.", y)
    y = draw_step(pdf, 1, "Escolha o tipo", "Defina Receita ou Despesa. Essa escolha altera o cálculo do saldo.", y)
    y = draw_step(pdf, 2, "Preencha o valor", "Informe apenas o valor; o campo aplica máscara monetária e valida a tipagem.", y)
    y = draw_step(pdf, 3, "Descreva e categorize", "Use uma descrição reconhecível e a categoria correta para melhorar gráficos e filtros.", y)
    y = draw_step(pdf, 4, "Confirme a data", "Ajuste compras passadas antes de salvar e use observações apenas quando ajudarem na revisão.", y)
    y = draw_two_cards(pdf, [
        ("Despesas fixas", "Cadastre aluguel, assinaturas e contas recorrentes com vencimento."),
        ("Orçamento", "Compare compromissos recorrentes com a renda prevista antes de assumir novos gastos."),
    ], y)
    y = draw_callout(pdf, "Evite duplicidade", "Compras parceladas devem ser registradas no fluxo do cartão. Não lance a mesma compra novamente como transação comum.", y, AMBER_SOFT, AMBER)
    y = draw_paragraph(pdf, "Checklist semanal", MARGIN_X, y, CONTENT_WIDTH, CARD_TITLE) - pt(4)
    y = draw_bullet(pdf, "Conferir entradas e saídas relevantes.", y)
    y = draw_bullet(pdf, "Corrigir categoria ou data de itens lançados com pressa.", y)
    draw_bullet(pdf, "Revisar vencimentos e desativar recorrências encerradas.", y)

    # Planning
    next_page(pdf)
    y = draw_header(pdf, "Planejamento", "04", version, 6)
    y = draw_title(pdf, "Cartões, investimentos e metas", "Separe crédito, patrimônio e objetivos para não misturar compromissos com progresso.", y)
    y = draw_paragraph(pdf, "Cartões", MARGIN_X, y, CONTENT_WIDTH, CARD_TITLE) - pt(4)
    y = draw_bullet(pdf, "Cadastre bandeira, limite, fechamento e vencimento.", y)
    y = draw_bullet(pdf, "Informe valor total, parcelas e data. O sistema calcula o valor de cada parcela.", y)
    y = draw_bullet(pdf, "Limite disponível não é renda; acompanhe também as parcelas futuras.", y)
    y -= pt(2)
    y = draw_paragraph(pdf, "Investimentos", MARGIN_X, y, CONTENT_WIDTH, CARD_TITLE) - pt(4)
    y = draw_bullet(pdf, "Informe tipo, instituição, aporte inicial, vencimento e retorno esperado quando aplicável.", y, BLUE)
    y = draw_bullet(pdf, "Registre aportes, retiradas e rendimentos para preservar o histórico.", y, BLUE)
    y = draw_bullet(pdf, "Projeções não substituem o extrato da instituição financeira.", y, BLUE)
    y -= pt(2)
    y = draw_paragraph(pdf, "Metas", MARGIN_X, y, CONTENT_WIDTH, CARD_TITLE) - pt(4)
    y = draw_bullet(pdf, "Defina título objetivo, valor-alvo e prazo realista.", y, AMBER)
    y = draw_bullet(pdf, "Atualize o progresso somente com dinheiro realmente reservado.", y, AMBER)
    y = draw_bullet(pdf, "Ao concluir, finalize a meta para manter o painel limpo.", y, AMBER)
    draw_callout(pdf, "Informação, não recomendação", "Insights e projeções ajudam na organização, mas não constituem recomendação de investimento ou crédito.", y, BLUE_SOFT, BLUE)

    # Analysis
    next_page(pdf)
    y = draw_header(pdf, "Análise", "05", version, 7)
    y = draw_title(pdf, "Relatórios, insights e notificações", "Transforme registros em informação útil e exporte somente quando necessário.", y)
    y = draw_step(pdf, 1, "Defina o período", "Selecione mês, ano ou intervalo disponível antes de gerar o relatório.", y)
    y = draw_step(pdf, 2, "Escolha o formato", "Use planilha para análise, CSV para interoperabilidade e HTML para visualização pronta.", y)
    y = draw_step(pdf, 3, "Proteja o arquivo", "Relatórios podem conter dados sensíveis. Evite pastas públicas e compartilhamentos desnecessários.", y)
    y = draw_two_cards(pdf, [
        ("Insights", "Destacam padrões dos seus dados, como pressão de despesas ou evolução de metas."),
        ("Notificações", "Centralizam avisos e podem ser marcadas como lidas individualmente ou em conjunto."),
    ], y)
    y = draw_callout(pdf, "Exportação segura", "A planilha neutraliza fórmulas perigosas inseridas em descrições. Mesmo assim, confirme período e conteúdo antes de compartilhar.", y)
    y = draw_paragraph(pdf, "Quando usar cada recurso", MARGIN_X, y, CONTENT_WIDTH, CARD_TITLE) - pt(4)
    y = draw_bullet(pdf, "Dashboard: acompanhamento rápido e frequente.", y)
    y = draw_bullet(pdf, "Insights: interpretação orientada por padrões.", y)
    draw_bullet(pdf, "Relatório: auditoria, arquivo, contabilidade ou análise detalhada.", y)

    # Collaboration
    next_page(pdf)
    y = draw_header(pdf, "Colaboração", "06", version, 8)
    y = draw_title(pdf, "Espaços compartilhados e assinatura", "Organize finanças em conjunto mantendo papéis e limites claros.", y)
    y = draw_step(pdf, 1, "Crie o espaço", "Use um nome que identifique a finalidade, como Casa, Viagem ou Projeto.", y)
    y = draw_step(pdf, 2, "Convide por e-mail", "A pessoa precisa usar o endereço associado à conta DashDaily.", y)
    y = draw_step(pdf, 3, "Escolha o papel", "Proprietário administra, Editor altera dados e Visualizador apenas consulta.", y)
    y = draw_step(pdf, 4, "Revise membros", "Remova acessos quando a colaboração terminar e conceda apenas o nível necessário.", y)
    y = draw_two_cards(pdf, [
        ("Plano gratuito", "Inclui recursos essenciais com limites seguros de uso."),
        ("Planos superiores", "Podem ampliar limites, relatórios e suporte conforme a oferta ativa."),
    ], y)
    y = draw_two_cards(pdf, [
        ("Checkout", "A contratação abre o fluxo seguro do provedor de pagamento."),
        ("Portal", "Use o portal de assinatura para consultar e gerenciar a cobrança."),
    ], y)
    draw_callout(pdf, "Cobrança protegida", "Dados completos de cartão devem ser informados somente no ambiente seguro do provedor de pagamento.", y)

    # Profile
    next_page(pdf)
    y = draw_header(pdf, "Conta", "07", version, 9)
    y = draw_title(pdf, "Preferências, perfil e privacidade", "Personalize a experiência sem perder o controle sobre sessão e dados.", y)
    y = draw_two_cards(pdf, [
        ("Idioma e moeda", "Alteram a apresentação, sem converter automaticamente lançamentos existentes."),
        ("Insights financeiros", "Ative ou desative análises baseadas nos seus registros."),
    ], y)
    y = draw_two_cards(pdf, [
        ("Notificações", "Controle avisos no app, por e-mail e push conforme a disponibilidade."),
        ("Perfil", "Atualize nome e imagem. Endereços de imagem devem usar HTTPS."),
    ], y)
    y = draw_paragraph(pdf, "Troca de senha", MARGIN_X, y, CONTENT_WIDTH, CARD_TITLE) - pt(4)
    y = draw_step(pdf, 1, "Abra Perfil", "Localize a seção de segurança da conta.", y)
    y = draw_step(pdf, 2, "Informe a senha atual", "Isso comprova que a sessão pertence a você.", y)
    y = draw_step(pdf, 3, "Escolha uma senha nova", "Use ao menos 8 caracteres e não repita a senha anterior.", y)
    y = draw_step(pdf, 4, "Entre novamente", "A troca revoga sessões anteriores e protege aparelhos antigos.", y)
    draw_callout(pdf, "Sessões protegidas", "Na Web, a renovação usa cookie HttpOnly, Secure e SameSite Strict. No Android, o aplicativo usa o armazenamento seguro do sistema.", y)

    # Install
    next_page(pdf)
    y = draw_header(pdf, "Android", "08", version, 10)
    y = draw_title(pdf, "Instalação segura no Android", f"A versão {version} é distribuída como APK oficial e assinada com chave de produção.", y)
    y = draw_callout(
        pdf,
        "Download oficial",
        f"Baixe <b>dashdaily-mobile-{version}-android.apk</b> somente em github.com/DevKaue/DashDaily-Releases/releases.",
        y,
        BLUE_SOFT,
        BLUE,
        pt(37),
    )
    y = draw_step(pdf, 1, "Baixe no telefone", "Abra a release oficial e toque no arquivo APK correspondente à versão publicada.", y)
    y = draw_step(pdf, 2, "Autorize a fonte", "O Android pode pedir permissão temporária para o navegador ou gerenciador de arquivos instalar apps.", y)
    y = draw_step(pdf, 3, "Confirme a instalação", "Revise o nome DashDaily, conclua a instalação e revogue a permissão de fonte quando não precisar mais.", y)
    y = draw_step(pdf, 4, "Entre na conta", "Use as mesmas credenciais da Web. Seus dados permanecem sincronizados pela API oficial.", y)
    y = draw_callout(
        pdf,
        "Migração única da 1.1.1",
        "Desinstale a 1.1.1 antes de instalar a 1.2.0 porque a assinatura de produção foi criada nesta versão. Seus dados do servidor permanecem; será necessário entrar novamente.",
        y,
        AMBER_SOFT,
        AMBER,
        pt(39),
    )
    draw_paragraph(pdf, f"Pacote: com.dashdaily.app  /  Versão: {version}  /  Código: {version_code}", MARGIN_X, y, CONTENT_WIDTH, SMALL)

    # Updates
    next_page(pdf)
    y = draw_header(pdf, "Atualizações", "09", version, 11)
    y = draw_title(pdf, "Atualizações integradas ao aplicativo", "Depois da versão 1.2.0, você não precisa procurar manualmente um novo APK.", y)
    y = draw_step(pdf, 1, "Verificação automática", "O app consulta o catálogo oficial ao abrir e periodicamente quando volta ao primeiro plano.", y)
    y = draw_step(pdf, 2, "Resumo das melhorias", "Uma tela mostra versão, tamanho, descrição e lista das mudanças antes do download.", y)
    y = draw_step(pdf, 3, "Download interno", "Toque em Atualizar agora. O APK é baixado dentro do DashDaily com indicador de progresso.", y)
    y = draw_step(pdf, 4, "Instalação protegida", "O aplicativo abre o instalador do Android, que confere a assinatura e solicita sua confirmação final.", y)
    y = draw_two_cards(pdf, [
        ("Atualização opcional", "Pode ser adiada com Mais tarde e reaparecer em uma verificação futura."),
        ("Atualização necessária", "É usada quando versões antigas deixam de ser compatíveis ou seguras."),
    ], y)
    y = draw_callout(pdf, "Por que existe uma confirmação?", "O Android não permite que um APK comum se reinstale silenciosamente. A confirmação final protege o aparelho contra substituições indesejadas.", y, BLUE_SOFT, BLUE, pt(37))
    y = draw_paragraph(pdf, "Canal oficial", MARGIN_X, y, CONTENT_WIDTH, CARD_TITLE) - pt(4)
    y = draw_bullet(pdf, "Catálogo: raw.githubusercontent.com/DevKaue/DashDaily-Releases", y)
    y = draw_bullet(pdf, "Arquivos: github.com/DevKaue/DashDaily-Releases/releases", y)
    draw_bullet(pdf, "O Android recusa uma atualização cuja assinatura não corresponda ao app instalado.", y)

    # Troubleshooting
    next_page(pdf)
    y = draw_header(pdf, "Ajuda", "10", version, 12)
    y = draw_title(pdf, "Solução de problemas", "Diagnóstico rápido sem expor informações sensíveis.", y)
    rows = [
        ["Sintoma", "O que fazer"],
        ["Não consigo entrar", "Confirme o e-mail, revise a senha e use Esqueci minha senha. Evite tentativas repetidas."],
        ["API iniciando", "Aguarde até 75 segundos no primeiro acesso. O serviço gratuito pode despertar após inatividade."],
        ["Dashboard não abre", "Atualize a página. Se voltar ao login, entre novamente porque a sessão expirou."],
        ["Instalação bloqueada", "Autorize temporariamente a fonte usada e confirme que o arquivo veio da release oficial."],
        ["App não instalado sobre 1.1.1", "Desinstale a 1.1.1 e instale a 1.2.0. Essa migração de assinatura ocorre uma única vez."],
        ["Atualização não apareceu", "Confirme a internet, reabra o app e aguarde a próxima verificação automática."],
    ]
    y = draw_simple_table(pdf, rows, y, [pt(45), CONTENT_WIDTH - pt(45)])
    y = draw_callout(pdf, "Ao pedir suporte", "Informe Web ou Android, a tela, os passos e o resultado esperado. Nunca envie senhas, tokens, dados completos de cartão ou informações desnecessárias.", y, RED_SOFT, RED, pt(37))
    y = draw_paragraph(pdf, "Canais oficiais", MARGIN_X, y, CONTENT_WIDTH, CARD_TITLE) - pt(4)
    y = draw_bullet(pdf, "Web: https://dashdaily-web.vercel.app", y)
    y = draw_bullet(pdf, "Releases: https://github.com/DevKaue/DashDaily-Releases/releases", y)
    draw_bullet(pdf, "Status da API: https://dashdaily-api.onrender.com/health", y)

    # Current release
    next_page(pdf)
    y = draw_header(pdf, "Novidades", "11", version, 13)
    y = draw_title(pdf, f"O que mudou na versão {version}", catalog["summary"], y)
    y = draw_paragraph(pdf, catalog["title"], MARGIN_X, y, CONTENT_WIDTH, CARD_TITLE) - pt(5)
    for improvement in catalog["improvements"]:
        y = draw_bullet(pdf, improvement, y)
    y -= pt(3)
    y = draw_callout(
        pdf,
        "Identificação do APK",
        f"Arquivo: dashdaily-mobile-{version}-android.apk<br/>Tamanho: {android['sizeBytes'] / 1_048_576:.1f} MB<br/>Pacote: {android['packageName']}  /  Código: {version_code}",
        y,
        GREEN_SOFT,
        GREEN,
        pt(42),
    )
    y = draw_paragraph(pdf, "SHA-256", MARGIN_X, y, CONTENT_WIDTH, CARD_TITLE) - pt(3)
    y = draw_paragraph(pdf, android["sha256"], MARGIN_X, y, CONTENT_WIDTH, MONO) - pt(8)
    y = draw_callout(pdf, "Você está pronto", "Comece pequeno: registre renda, despesas principais e uma meta. A qualidade das análises cresce junto com a consistência dos seus registros.", y, BLUE_SOFT, BLUE, pt(37))
    draw_paragraph(pdf, f"Release publicada em {published_at}.", MARGIN_X, y, CONTENT_WIDTH, SMALL)

    pdf.save()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=Path("releases/latest.json"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    output = args.output or Path("dist") / f"Guia_de_Utilizacao_DashDaily_{catalog['version']}.pdf"
    build_guide(catalog, output)
    print(output.resolve())


if __name__ == "__main__":
    main()
