import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

# Define content data
PROJECT_NAME = "Нейротуннель «Туннель Состояний» / Neurotunnel: The State Tunnel"
TRACK = "Пространственные и предметные индустрии (Пространственные решения, арт-инсталляции, средовой дизайн)"

TEAM = [
    {
        "role": "Главный архитектор (Конструктив и Пространство)",
        "name": "Алёна Левицкая",
        "bio": "Руководитель архитектурного бюро «СТРУКТУРА» (с 2015 г.), член Союза архитекторов Москвы с 2009 г. Лицензирована Минкультуры РФ на работу с объектами культурного наследия. Автор концепций пространственной интеграции медиа-арта, куратор образовательных программ в МАРХИ."
    },
    {
        "role": "Технологический директор / Физик (Сенсоры, Оптика и Звук)",
        "name": "Валерий Латыпов",
        "bio": "Магистр наук по физике конденсированного состояния (НИЯУ МИФИ). Специалист в области квантовой оптики, акустики и сенсорных интерфейсов. Разработчик систем бесконтактного мониторинга физиологических показателей на основе rPPG (фотоплетизмографии) и компьютерного зрения."
    }
]

CONCEPT_PROBLEM = (
    "Современный житель мегаполиса находится в состоянии хронического информационного перегруза и стресса. "
    "Приходя в культурные пространства (музеи, театры, галереи), человек приносит этот ментальный шум с собой. "
    "Его восприятие заблокировано, он не готов к глубокому эмоциональному контакту с искусством. "
    "Большинство существующих арт-объектов предлагают статичный или усредненный опыт для всей массы посетителей, "
    "не адаптируясь под психоэмоциональное состояние конкретного зрителя."
)

CONCEPT_SOLUTION = (
    "«Нейротуннель» спроектирован в новой концепции Эмотех (Emotech / Emotional Tech), направленной на создание "
    "эмоционально отзывчивых терапевтических сред. Проект представляет собой физический шлюз-фильтр в виде цилиндрического "
    "коридора или прямоугольной призмы с бесшовными LED-экранами на стыках. Проходя сквозь него, посетитель бесконтактно "
    "сканируется встроенными сенсорами. Система определяет уровень стресса, усталости или хаоса и перестраивает под него "
    "световое поле, направленный звук (бинауральные ритмы) и генеративную графику.\n\n"
    "Человек проходит через иммерсивный сценарий жизненного цикла (от «рождения», через накопление опыта к «символической смерти» — "
    "очищению белым светом, и психоэмоциональному катарсису/возрождению в зале адаптации)."
)

USPS = [
    {
        "title": "Абсолютная бесконтактность",
        "desc": "Никаких датчиков на теле. Пульс и частота дыхания считываются ИК- и RGB-камерами по микро-колебаниям цвета кожи лица (rPPG), мимический тонус — алгоритмами Face Mesh, траектория движения — датчиками LiDAR."
    },
    {
        "title": "Акустический барьер",
        "desc": "Направленные звуковые прожекторы Audio Spotlight (угол направленности 3-5°) полностью изолируют человека от внешнего шума улицы или холла, создавая индивидуальную звуковую зону для каждого посетителя."
    },
    {
        "title": "Социальная синестезия (Индивидуальные ауры в толпе)",
        "desc": "При групповом проходе туннель не создает какофонии. Он проецирует индивидуальные световые кольца («ауры») вокруг каждого пешехода. При сближении людей цвета их аур плавно смешиваются (lerp-эффект), создавая гармонизирующий визуальный диалог."
    },
    {
        "title": "Абсолютная конфиденциальность (Privacy by Design)",
        "desc": "Все биометрические показатели обрабатываются исключительно в оперативной памяти «на лету» без сохранения на диски или отправки в облачные сервисы, полностью отвечая требованиям о защите персональных данных."
    },
    {
        "title": "Визионерское масштабирование",
        "desc": "Концепция масштабируется от локального шлюза в музее (ГЭС-2) до свето-акустических коридоров на мостах Москвы (включая переход от Храма Христа Спасителя к Красному Октябрю) и синхронизации с медиа-фасадами Москва-Сити и линиями метро в виде единой городской «Нейросети Мегаполиса»."
    }
]

TECH_SPECS = [
    ("Конструктив", "Облегченный алюминиевый модульный каркас быстрого монтажа (время сборки — 4 часа)."),
    ("Система отображения", "Гибкие бесшовные LED-экраны высокого разрешения (шаг пикселя 1.8-2.5 мм) на полу, потолке и стенах."),
    ("Сенсорный массив", "ИК-камеры, RGB-камеры, лазерные сенсоры LiDAR (высокоточное определение координат X/Y/Z)."),
    ("Звуковая система", "Ультранаправленные звуковые прожекторы Audio Spotlight для изоляции звуковых зон."),
    ("Программное обеспечение", "TouchDesigner / Unreal Engine 5 (генеративная графика), WebAudio API / MaxMSP (генерация бинауральных ритмов 6Гц-12Гц на несущей частоте 150Гц).")
]

LINKS = [
    ("Сайт-презентация проекта (Demo-лендинг)", "https://nejrofest-tunnel.vercel.app"),
    ("Видео-презентация проекта (3D Walkthrough)", "https://nejrofest-tunnel.vercel.app/images/walkthrough.mp4"),
    ("Схема оборудования и чертеж (blueprint)", "https://nejrofest-tunnel.vercel.app/images/blueprint.png"),
    ("Вид сбоку (архитектурная интеграция)", "https://nejrofest-tunnel.vercel.app/images/side_view.png"),
    ("Вид изнутри (световая среда)", "https://nejrofest-tunnel.vercel.app/images/pov_inside.png")
]


def create_docx(filename):
    doc = Document()
    
    # Page setup
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Styles
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Arial'
    style_normal.font.size = Pt(11)
    style_normal.paragraph_format.line_spacing = 1.15
    style_normal.paragraph_format.space_after = Pt(6)

    # Title
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run_title = title.add_run(PROJECT_NAME.upper())
    run_title.font.name = 'Arial'
    run_title.font.size = Pt(18)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(15, 23, 42) # Slate 900
    title.paragraph_format.space_after = Pt(2)

    subtitle = doc.add_paragraph()
    run_sub = subtitle.add_run("Заявка на участие в акселераторе #Нейрофест2026")
    run_sub.font.name = 'Arial'
    run_sub.font.size = Pt(11)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(212, 175, 55) # Gold
    subtitle.paragraph_format.space_after = Pt(18)

    # Horizontal Divider Line
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_after = Pt(12)
    p_div_border = OxmlElement('w:pBdr')
    bottom_border = OxmlElement('w:bottom')
    bottom_border.set(qn('w:val'), 'single')
    bottom_border.set(qn('w:sz'), '12')
    bottom_border.set(qn('w:space'), '1')
    bottom_border.set(qn('w:color'), 'CCCCCC')
    p_div_border.append(bottom_border)
    p_div._p.get_or_add_pPr().append(p_div_border)

    def add_section_heading(text):
        h = doc.add_paragraph()
        run = h.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(15, 23, 42) # Slate 900
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        return h

    # 1. Track
    add_section_heading("НАПРАВЛЕНИЕ / НОМИНАЦИЯ")
    p = doc.add_paragraph()
    p.add_run(TRACK).font.bold = True
    p.paragraph_format.space_after = Pt(12)

    # 2. Problem
    add_section_heading("1. КАКУЮ ПРОБЛЕМУ РЕШАЕТ ПРОЕКТ?")
    p = doc.add_paragraph(CONCEPT_PROBLEM)
    p.paragraph_format.space_after = Pt(12)

    # 3. Solution
    add_section_heading("2. СУТЬ РЕШЕНИЯ И КОНЦЕПЦИЯ")
    p = doc.add_paragraph(CONCEPT_SOLUTION)
    p.paragraph_format.space_after = Pt(12)

    # 4. USPs
    add_section_heading("3. УНИКАЛЬНОСТЬ И ТЕХНОЛОГИЧЕСКАЯ НОВИЗНА (УТП)")
    for i, usp in enumerate(USPS, 1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.2)
        run_title = p.add_run(f"3.{i}. {usp['title']}: ")
        run_title.bold = True
        run_title.font.color.rgb = RGBColor(15, 23, 42)
        p.add_run(usp['desc'])
        p.paragraph_format.space_after = Pt(6)

    # 5. Tech Specs Table
    add_section_heading("4. ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ И ОБОРУДОВАНИЕ")
    table = doc.add_table(rows=1, cols=2)
    table.autofit = False
    
    # Style table
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        '<w:tblBorders %s>'
        '<w:top w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        '<w:left w:val="none"/>'
        '<w:right w:val="none"/>'
        '<w:insideV w:val="none"/>'
        '</w:tblBorders>' % nsdecls('w')
    )
    tblPr.append(borders)

    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Компонент'
    hdr_cells[1].text = 'Техническое описание'
    for cell in hdr_cells:
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(15, 23, 42)
        cell.width = Inches(2.2) if cell == hdr_cells[0] else Inches(4.8)

    for item, desc in TECH_SPECS:
        row_cells = table.add_row().cells
        row_cells[0].text = item
        row_cells[0].paragraphs[0].runs[0].font.bold = True
        row_cells[1].text = desc
        row_cells[0].width = Inches(2.2)
        row_cells[1].width = Inches(4.8)
        
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 6. Team
    add_section_heading("5. КОМАНДА ПРОЕКТА")
    for t in TEAM:
        p = doc.add_paragraph()
        run_name = p.add_run(f"{t['name']} — {t['role']}\n")
        run_name.bold = True
        run_name.font.color.rgb = RGBColor(15, 23, 42)
        run_bio = p.add_run(t['bio'])
        run_bio.font.size = Pt(10)
        run_bio.font.color.rgb = RGBColor(71, 85, 105) # Slate 600
        p.paragraph_format.space_after = Pt(10)

    # 7. Links
    add_section_heading("6. МАТЕРИАЛЫ И ССЫЛКИ ДЛЯ ПРИКРЕПЛЕНИЯ К ЗАЯВКЕ")
    for name, url in LINKS:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.2)
        p.paragraph_format.space_after = Pt(4)
        run_bullet = p.add_run("•  ")
        run_bullet.bold = True
        run_bullet.font.color.rgb = RGBColor(212, 175, 55)
        run_name = p.add_run(f"{name}: ")
        run_name.bold = True
        run_url = p.add_run(url)
        run_url.font.color.rgb = RGBColor(14, 165, 233) # Sky 500
        run_url.underline = True

    # Footer note
    doc.add_paragraph().paragraph_format.space_after = Pt(18)
    p_foot = doc.add_paragraph()
    p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_foot = p_foot.add_run("Документ подготовлен автоматически для отправки партнёрам и соавторам проекта.")
    run_foot.font.size = Pt(8.5)
    run_foot.font.italic = True
    run_foot.font.color.rgb = RGBColor(148, 163, 184) # Slate 400

    doc.save(filename)
    print(f"Word document saved to {filename}")


def create_pdf(filename):
    # Setup document
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    # Font registrations
    pdfmetrics.registerFont(TTFont('Arial', '/System/Library/Fonts/Supplemental/Arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', '/System/Library/Fonts/Supplemental/Arial Bold.ttf'))

    # Stylesheet
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#d4af37'),
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'DocH1',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )

    usp_title_style = ParagraphStyle(
        'DocUSPTitle',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=4,
        spaceAfter=2,
        leftIndent=10
    )

    usp_desc_style = ParagraphStyle(
        'DocUSPDesc',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor('#475569'),
        spaceAfter=6,
        leftIndent=10
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#0f172a')
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#334155')
    )

    table_cell_normal = ParagraphStyle(
        'TableCellNormal',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#475569')
    )

    link_label_style = ParagraphStyle(
        'LinkLabel',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155'),
        leftIndent=10
    )

    link_url_style = ParagraphStyle(
        'LinkURL',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#0ea5e9'),
        leftIndent=10,
        spaceAfter=4
    )

    story = []

    # Title & Header
    story.append(Paragraph(PROJECT_NAME.upper(), title_style))
    story.append(Paragraph("Заявка на участие в акселераторе #Нейрофест2026", subtitle_style))
    
    # Custom Divider Line
    divider = Table([['']], colWidths=[505], rowHeights=[1.5])
    divider.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#CCCCCC')),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 10))

    # Track
    story.append(Paragraph("НАПРАВЛЕНИЕ / НОМИНАЦИЯ", h1_style))
    story.append(Paragraph(f"<b>{TRACK}</b>", body_style))

    # 1. Problem
    story.append(Paragraph("1. КАКУЮ ПРОБЛЕМУ РЕШАЕТ ПРОЕКТ?", h1_style))
    story.append(Paragraph(CONCEPT_PROBLEM, body_style))

    # 2. Solution
    story.append(Paragraph("2. СУТЬ РЕШЕНИЯ И КОНЦЕПЦИЯ", h1_style))
    # Replace newlines with break tags for ReportLab Paragraph compatibility
    sol_html = CONCEPT_SOLUTION.replace('\n', '<br/>')
    story.append(Paragraph(sol_html, body_style))

    # 3. USPs
    story.append(Paragraph("3. УНИКАЛЬНОСТЬ И ТЕХНОЛОГИЧЕСКАЯ НОВИЗНА (УТП)", h1_style))
    for i, usp in enumerate(USPS, 1):
        story.append(Paragraph(f"3.{i}. {usp['title']}", usp_title_style))
        story.append(Paragraph(usp['desc'], usp_desc_style))

    story.append(Spacer(1, 6))

    # 4. Tech Specs Table
    story.append(Paragraph("4. ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ И ОБОРУДОВАНИЕ", h1_style))
    
    table_data = [
        [Paragraph("Компонент", table_header_style), Paragraph("Техническое описание", table_header_style)]
    ]
    for item, desc in TECH_SPECS:
        table_data.append([
            Paragraph(item, table_cell_bold),
            Paragraph(desc, table_cell_normal)
        ])
    
    tech_table = Table(table_data, colWidths=[130, 375])
    tech_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(tech_table)
    story.append(Spacer(1, 10))

    # 5. Team
    story.append(Paragraph("5. КОМАНДА ПРОЕКТА", h1_style))
    for t in TEAM:
        team_text = f"<b>{t['name']}</b> — {t['role']}<br/><font color='#475569' size='8.5'>{t['bio']}</font>"
        story.append(Paragraph(team_text, body_style))

    # 6. Links
    story.append(Paragraph("6. МАТЕРИАЛЫ И ССЫЛКИ ДЛЯ ЗАЯВКИ", h1_style))
    for name, url in LINKS:
        story.append(Paragraph(f"•  <b>{name}</b>", link_label_style))
        story.append(Paragraph(f"<a href='{url}'>{url}</a>", link_url_style))

    # Build PDF
    doc.build(story)
    print(f"PDF document saved to {filename}")


if __name__ == "__main__":
    output_docx = "/Volumes/Genius Art/Antigravity/nejrofest-tunnel/nejrotonnel_zayavka.docx"
    output_pdf = "/Volumes/Genius Art/Antigravity/nejrofest-tunnel/nejrotonnel_zayavka.pdf"
    
    create_docx(output_docx)
    create_pdf(output_pdf)
