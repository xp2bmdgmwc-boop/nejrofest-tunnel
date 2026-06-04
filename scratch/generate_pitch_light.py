import os
import sys
from PIL import Image

from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Dimensions (Points)
PDF_W = 960
PDF_H = 540

# Colors
COLOR_BG = "#FFFFFF"
COLOR_TEXT_MAIN = "#1E293B"  # Slate 800 (very dark grey)
COLOR_TEXT_MUTED = "#64748B" # Slate 500 (medium grey)
COLOR_GOLD = "#B58A3D"       # Sophisticated Gold
COLOR_BORDER = "#E2E8F0"     # Slate 200 (light grey)
COLOR_CARD_BG = "#F8FAFC"    # Slate 50 (very light grey)
COLOR_LINE = "#64748B"       # Slate 500 for timelines

# Register Arial font for Cyrillic support
# ReportLab needs a registered font file to draw Russian characters correctly.
pdfmetrics.registerFont(TTFont('Arial', '/System/Library/Fonts/Supplemental/Arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', '/System/Library/Fonts/Supplemental/Arial Bold.ttf'))

# Drawing Helpers
def pdf_rect(c, x, y_top, w, h, fill_color, stroke_color=None, border_w=1, rx=0, ry=0):
    c.saveState()
    c.setFillColor(HexColor(fill_color))
    y = PDF_H - y_top - h
    if stroke_color:
        c.setStrokeColor(HexColor(stroke_color))
        c.setLineWidth(border_w)
        stroke = True
    else:
        c.setStrokeColor(HexColor(fill_color))
        c.setLineWidth(0)
        stroke = False
    
    if rx > 0 or ry > 0:
        c.roundRect(x, y, w, h, rx, fill=True, stroke=stroke)
    else:
        c.rect(x, y, w, h, fill=True, stroke=stroke)
    c.restoreState()

def pdf_text(c, x, y_top, text, font_name="Arial", font_size=12, color=COLOR_TEXT_MAIN, align="left", line_height=1.2, max_w=None):
    c.saveState()
    c.setFont(font_name, font_size)
    c.setFillColor(HexColor(color))
    
    # Split input by explicit newlines
    paragraphs = text.split('\n')
    all_lines = []
    
    for para in paragraphs:
        if not para.strip() and len(para) == 0:
            all_lines.append("")
            continue
            
        if max_w is None:
            all_lines.append(para)
        else:
            words = para.split(' ')
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word]) if current_line else word
                width = c.stringWidth(test_line, font_name, font_size)
                if width <= max_w:
                    current_line.append(word)
                else:
                    if current_line:
                        all_lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        all_lines.append(word)
            if current_line:
                all_lines.append(' '.join(current_line))
                
    for i, line in enumerate(all_lines):
        # Shift slightly down because drawString draws from baseline
        curr_y = PDF_H - y_top - (i * font_size * line_height) - font_size * 0.8
        if line == "":
            continue
        if align == "center":
            c.drawCentredString(x, curr_y, line)
        elif align == "right":
            c.drawRightString(x, curr_y, line)
        else:
            c.drawString(x, curr_y, line)
    c.restoreState()
    return len(all_lines) * font_size * line_height

def pdf_line(c, x1, y1_top, x2, y2_top, stroke_color=COLOR_BORDER, border_w=1):
    c.saveState()
    c.setStrokeColor(HexColor(stroke_color))
    c.setLineWidth(border_w)
    c.line(x1, PDF_H - y1_top, x2, PDF_H - y2_top)
    c.restoreState()

def draw_pdf_image_fit(c, img_path, left_px, top_px, max_w_px, max_h_px):
    if not os.path.exists(img_path):
        print(f"Warning: image not found at {img_path}")
        return
    try:
        with Image.open(img_path) as img:
            w, h = img.size
        aspect = w / h
        box_aspect = max_w_px / max_h_px
        if aspect > box_aspect:
            fit_w = max_w_px
            fit_h = max_w_px / aspect
        else:
            fit_h = max_h_px
            fit_w = max_h_px * aspect
        off_x = (max_w_px - fit_w) / 2
        off_y = (max_h_px - fit_h) / 2
        
        rl_y = PDF_H - (top_px + off_y + fit_h)
        c.drawImage(img_path, left_px + off_x, rl_y, width=fit_w, height=fit_h)
    except Exception as e:
        print(f"Error loading image {img_path} in PDF: {e}")

# Text Translations Map
TEXTS = {
    'ru': {
        's1_title': "Нейротуннель\nТуннель состояний",
        's1_sub': "Адаптивная свето-акустическая среда для учреждений культуры",
        's1_format': "Формат: архитектурная инсталляция и пространственный сервис",
        's1_authors': "Авторы: Алёна Левицкая (архитектор, АБ «Структура»)\nВалерий Латыпов (физик, визуальный художник)",
        
        's2_title': "Идея",
        's2_text': "Шлюз между шумом города и вниманием к искусству.\n\nПосетитель приходит в музей или театр перегруженным, и восприятие закрыто ещё до встречи с экспозицией.\n\nНейротуннель решает это пространственно: за 60 секунд среда мягко возвращает человеку баланс — бесконтактно, через управляемый свет, звук и направленную акустику.",
        
        's3_title': "Что мы видим на рынке",
        's3_sub': "Три ограничения существующих решений:",
        's3_c1_title': "Медленный рост",
        's3_c1_text': "Прикладной ИИ и иммерсивные форматы в учреждениях культуры развиваются медленно.",
        's3_c2_title': "Без коррекции",
        's3_c2_text': "Мировые аналоги (Aura, Tunnel of Sentient Light) визуализируют состояние, но не корректируют его.",
        's3_c3_title': "Правовой барьер",
        's3_c3_text': "Решения с нейроинтерфейсами и хранением биометрии плохо совместимы со 152-ФЗ.",
        
        's4_title': "Аудитория и масштаб",
        's4_b2b_title': "B2B",
        's4_b2b_text': "Учреждения культуры: музеи, библиотеки, театры — новый формат опыта и повторные визиты.",
        's4_b2c_title': "B2C",
        's4_b2c_text': "Посетители: горожане 25–55 лет — осмысленный опыт, снятие напряжения, персонализация.",
        's4_b2g_title': "B2G",
        's4_b2g_text': "Город: администрации и девелоперы — точки притяжения и умная архитектура.",
        's4_target': "Ориентир: более 90 000 учреждений, десятки миллионов визитов в год.",
        
        's5_title': "Сценарий: 60 секунд",
        's5_step1_time': "0–5 сек",
        's5_step1_desc': "Приближение фиксирует LiDAR.",
        's5_step2_time': "5–15 сек",
        's5_step2_desc': "Вход и сканирование: пульс считывается по микроизменениям кожи (rPPG), эмоциональный тонус — по Face Mesh.",
        's5_step3_time': "15–50 сек",
        's5_step3_desc': "Свето-акустический кокон: LED-панели создают компенсирующее световое поле, Audio Spotlight — зону с бинауральными ритмами.",
        's5_step4_time': "50–60 сек",
        's5_step4_desc': "Выход: световая «перезагрузка» и QR-код с персональной видео-открыткой.",
        's5_throughput': "Пропускная способность одного звена — до 1 000 человек в час.",
        
        's6_title': "Четыре принципа",
        's6_p1_title': "Активная компенсация",
        's6_p1_desc': "Среда не зеркалит состояние, а мягко возвращает баланс.",
        's6_p2_title': "Бесконтактность",
        's6_p2_desc': "Без шлемов, датчиков и браслетов — диагностика на ходу.",
        's6_p3_title': "Privacy by Design",
        's6_p3_desc': "Биометрия не сохраняется, обработка только в оперативной памяти (152-ФЗ).",
        's6_p4_title': "Масштабируемость",
        's6_p4_desc': "От камерного 10-метрового модуля до 200-метрового пространства.",
        
        's7_title': "Позиционирование",
        's7_sub': "Сравнение по ключевым параметрам:",
        's7_col0': "Параметр",
        's7_col1': "Aura",
        's7_col2': "Tunnel of Sentient Light",
        's7_col3': "Нейротуннель",
        's7_r1_lbl': "Считывание",
        's7_r1_val1': "EEG и носимые датчики",
        's7_r1_val2': "Стационарные камеры",
        's7_r1_val3': "rPPG, бесконтактно",
        's7_r2_lbl': "Воздействие",
        's7_r2_val1': "Визуализирует состояние",
        's7_r2_val2': "Визуализирует состояние",
        's7_r2_val3': "Активная алгоритмическая компенсация",
        's7_r3_lbl': "Приватность",
        's7_r3_val1': "Хранит данные",
        's7_r3_val2': "Хранит данные",
        's7_r3_val3': "Обработка только в RAM",
        's7_r4_lbl': "Масштаб",
        's7_r4_val1': "Единый формат",
        's7_r4_val2': "Единый формат",
        's7_r4_val3': "Адаптивная архитектура от 10 до 200 м",
        
        's8_title': "Бизнес-модель",
        's8_h1': "Источники дохода",
        's8_t1': "Продажа B2B-модулей, лицензирование ПО, сервисные контракты, гранты (Сколково, ПФКИ), партнёрство брендов.",
        's8_h2': "Форматы и ориентировочный бюджет",
        's8_t2': "Сейчас готовы концепция, архитектурная разработка, ядро команды и сайт-витрина.",
        's8_c1_title': "Камерный",
        's8_c1_desc': "10×2,5×3 м — 8–15 млн ₽",
        's8_c2_title': "Тоннель 20 м",
        's8_c2_desc': "60–100 млн ₽",
        's8_c3_title': "Макро-формат",
        's8_c3_desc': "100–150 млн ₽",
        
        's9_title': "Команда и партнёры",
        's9_a_name': "Алёна Левицкая",
        's9_a_bio': "Архитектура и пространство. Основатель и руководитель архитектурного бюро «Структура». Преподаватель МАРХИ. Член Союза московских архитекторов.",
        's9_v_name': "Валерий Латыпов",
        's9_v_bio': "Технологическое видение. Инженер-физик (НИЯУ МИФИ), 20+ лет на стыке физики, искусства и звука. Спикер TEDx.",
        's9_p_title': "Целевые партнеры",
        's9_p_list': "АБ «Структура»\nГЭС-2\nТретьяковка, ГМИИ\nSber AI, Яндекс\nРГБ\nРосатом",
        
        's10_title': "Дорожная карта и запрос",
        's10_t1_date': "2026",
        's10_t1_text': "Концепция и MoU готовы, расширение команды, выбор пилотной площадки.",
        's10_t2_date': "Сентябрь 2026",
        's10_t2_text': "Лабораторный MVP и питч перед партнёрами.",
        's10_t3_date': "2026–2027",
        's10_t3_text': "Пилот «Камерного формата» в учреждении культуры.",
        's10_t4_date': "2027–2028",
        's10_t4_text': "Серийная B2B-версия.",
        's10_seek_title': "Что ищем",
        's10_seek1': "Технологическую экспертизу и менторство",
        's10_seek2': "Пилотную площадку",
        's10_seek3': "Финансирование первого пилота",
        's10_target_title': "Целевые ориентиры к 2027",
        's10_targets': [
            {'val': "94%", 'lbl': " восстановления баланса"},
            {'val': "NPS 90+", 'lbl': ""},
            {'val': "0", 'lbl': " случаев хранения биометрии"}
        ],
        's11_text': "Продолжение следует_"
    },
    'en': {
        's1_title': "Neurotunnel\nState Tunnel",
        's1_sub': "Adaptive light-acoustic environment for cultural institutions",
        's1_format': "Format: architectural installation and spatial service",
        's1_authors': "Authors: Alena Levitskaya (architect, AB \"Structure\")\nValery Latypov (physicist, visual artist)",
        
        's2_title': "Idea",
        's2_text': "A gateway between city noise and attention to art.\n\nVisitors arrive at a museum or theater overloaded, their perception closed before they even reach the exhibition.\n\nNeurotunnel solves this spatially: in 60 seconds, the environment gently restores the visitor's balance — contactlessly, via controlled light, sound, and directional acoustics.",
        
        's3_title': "Market Landscape",
        's3_sub': "Three limitations of existing solutions:",
        's3_c1_title': "Slow Growth",
        's3_c1_text': "Applied AI and immersive formats in cultural institutions are developing slowly.",
        's3_c2_title': "No Correction",
        's3_c2_text': "Global counterparts (Aura, Tunnel of Sentient Light) visualize the state but do not correct it.",
        's3_c3_title': "Legal Barrier",
        's3_c3_text': "Solutions with neurointerfaces and biometrics storage are poorly compatible with personal data protection laws (e.g. 152-FZ).",
        
        's4_title': "Audience & Scale",
        's4_b2b_title': "B2B",
        's4_b2b_text': "Cultural institutions: museums, libraries, theaters — new experience format and repeat visits.",
        's4_b2c_title': "B2C",
        's4_b2c_text': "Visitors: city residents aged 25–55 — mindful experience, stress relief, personalization.",
        's4_b2g_title': "B2G",
        's4_b2g_text': "City: administrations and developers — points of attraction and smart architecture.",
        's4_target': "Target: more than 90,000 institutions, tens of millions of visits per year.",
        
        's5_title': "Scenario: 60 seconds",
        's5_step1_time': "0–5 sec",
        's5_step1_desc': "Approach detected by LiDAR.",
        's5_step2_time': "5–15 sec",
        's5_step2_desc': "Entry & scanning: heart rate is detected via skin micro-changes (rPPG), emotional tone — via Face Mesh.",
        's5_step3_time': "15–50 sec",
        's5_step3_desc': "Light-acoustic cocoon: LED panels create a compensating light field, Audio Spotlight — a zone with binaural beats.",
        's5_step4_time': "50–60 sec",
        's5_step4_desc': "Exit: light \"reboot\" and a QR code with a personalized video postcard.",
        's5_throughput': "Throughput of one unit — up to 1,000 people per hour.",
        
        's6_title': "Four Principles",
        's6_p1_title': "Active Compensation",
        's6_p1_desc': "The environment does not mirror the state but gently restores balance.",
        's6_p2_title': "Contactless",
        's6_p2_desc': "No helmets, sensors, or bracelets — diagnostics on the go.",
        's6_p3_title': "Privacy by Design",
        's6_p3_desc': "Biometrics are not stored, processed strictly in RAM (GPDR/152-FZ compliance).",
        's6_p4_title': "Scalability",
        's6_p4_desc': "From a compact 10-meter module to a 200-meter space.",
        
        's7_title': "Positioning",
        's7_sub': "Comparison by key parameters:",
        's7_col0': "Parameter",
        's7_col1': "Aura",
        's7_col2': "Tunnel of Sentient Light",
        's7_col3': "Neurotunnel",
        's7_r1_lbl': "Sensing",
        's7_r1_val1': "EEG & wearable sensors",
        's7_r1_val2': "Stationary cameras",
        's7_r1_val3': "rPPG, contactless",
        's7_r2_lbl': "Impact",
        's7_r2_val1': "Visualizes the state",
        's7_r2_val2': "Visualizes the state",
        's7_r2_val3': "Active algorithmic compensation",
        's7_r3_lbl': "Privacy",
        's7_r3_val1': "Stores data",
        's7_r3_val2': "Stores data",
        's7_r3_val3': "RAM-only processing",
        's7_r4_lbl': "Scale",
        's7_r4_val1': "Fixed format",
        's7_r4_val2': "Fixed format",
        's7_r4_val3': "Adaptive architecture from 10 to 200 m",
        
        's8_title': "Business Model",
        's8_h1': "Revenue Sources",
        's8_t1': "Sales of B2B modules, software licensing, service contracts, grants, brand partnerships.",
        's8_h2': "Formats and Estimated Budget",
        's8_t2': "Concept, architectural design, core team, and showcase website are ready.",
        's8_c1_title': "Compact",
        's8_c1_desc': "10×2.5×3 m — ₽8–15M",
        's8_c2_title': "Tunnel 20 m",
        's8_c2_desc': "₽60–100M",
        's8_c3_title': "Macro format",
        's8_c3_desc': "₽100–150M",
        
        's9_title': "Team & Partners",
        's9_a_name': "Alena Levitskaya",
        's9_a_bio': "Architecture & space. Founder and head of the architectural bureau \"Structure\". MARCHI lecturer. Member of the Union of Moscow Architects.",
        's9_v_name': "Valery Latypov",
        's9_v_bio': "Technological vision. Engineer-physicist (MEPhI), 20+ years at the intersection of physics, art, and sound. TEDx speaker.",
        's9_p_title': "Target Partners",
        's9_p_list': "AB \"Structure\"\nGES-2\nTretyakov Gallery, Pushkin Museum\nSber AI, Yandex\nRussian State Library\nRosatom",
        
        's10_title': "Roadmap & Request",
        's10_t1_date': "2026",
        's10_t1_text': "Concept and MoU ready, team expansion, pilot site selection.",
        's10_t2_date': "September 2026",
        's10_t2_text': "Laboratory MVP and pitch to partners.",
        's10_t3_date': "2026–2027",
        's10_t3_text': "Pilot of \"Compact format\" in a cultural institution.",
        's10_t4_date': "2027–2028",
        's10_t4_text': "Serial B2B version.",
        's10_seek_title': "What we are looking for",
        's10_seek1': "Technological expertise and mentorship",
        's10_seek2': "Pilot site",
        's10_seek3': "Funding for the first pilot",
        's10_target_title': "Targets by 2027",
        's10_targets': [
            {'val': "94%", 'lbl': " balance restoration"},
            {'val': "NPS 90+", 'lbl': ""},
            {'val': "0", 'lbl': " cases of biometrics storage"}
        ],
        's11_text': "To be continued_"
    }
}

def draw_presentation(lang, filename):
    t = TEXTS[lang]
    c = canvas.Canvas(filename, pagesize=(PDF_W, PDF_H))
    
    # ----------------------------------------------------
    # SLIDE 1: Cover
    # ----------------------------------------------------
    pdf_rect(c, 0, 0, PDF_W, PDF_H, COLOR_BG)
    draw_pdf_image_fit(c, "images/cover_tunnel.png", 80, 80, 380, 380)
    
    pdf_text(c, 500, 80, t['s1_title'], font_name="Arial-Bold", font_size=40, color=COLOR_TEXT_MAIN, line_height=1.1)
    pdf_text(c, 500, 200, t['s1_sub'], font_name="Arial", font_size=15, color=COLOR_TEXT_MUTED, line_height=1.3, max_w=380)
    pdf_text(c, 500, 280, t['s1_format'], font_name="Arial", font_size=14, color=COLOR_TEXT_MUTED, max_w=380)
    
    pdf_text(c, 500, 380, t['s1_authors'], font_name="Arial", font_size=13, color=COLOR_TEXT_MUTED, line_height=1.4, max_w=380)
    c.showPage()
    
    # ----------------------------------------------------
    # SLIDE 2: Idea
    # ----------------------------------------------------
    pdf_rect(c, 0, 0, PDF_W, PDF_H, COLOR_BG)
    pdf_text(c, 80, 60, t['s2_title'], font_name="Arial-Bold", font_size=32, color=COLOR_TEXT_MAIN)
    pdf_text(c, 80, 140, t['s2_text'], font_name="Arial", font_size=15, color=COLOR_TEXT_MAIN, line_height=1.5, max_w=400)
    
    draw_pdf_image_fit(c, "scratch/extracted_img-003.png", 530, 0, 430, PDF_H)
    c.showPage()
    
    # ----------------------------------------------------
    # SLIDE 3: What we see on the market
    # ----------------------------------------------------
    pdf_rect(c, 0, 0, PDF_W, PDF_H, COLOR_BG)
    pdf_text(c, 80, 50, t['s3_title'], font_name="Arial-Bold", font_size=32, color=COLOR_TEXT_MAIN)
    
    # Image in the middle
    draw_pdf_image_fit(c, "scratch/extracted_img-010.png", 200, 110, 560, 170)
    
    # Subtitle above cards
    pdf_text(c, 80, 300, t['s3_sub'], font_name="Arial", font_size=14, color=COLOR_TEXT_MUTED)
    
    # 3 Cards at bottom
    card_w = 250
    card_h = 130
    gap = 25
    y_card = 330
    
    for idx, card_key in enumerate([('s3_c1_title', 's3_c1_text'), ('s3_c2_title', 's3_c2_text'), ('s3_c3_title', 's3_c3_text')]):
        x_card = 80 + idx * (card_w + gap)
        # Card background
        pdf_rect(c, x_card, y_card, card_w, card_h, COLOR_CARD_BG, stroke_color=COLOR_BORDER, rx=4, ry=4)
        # Left Accent bar
        pdf_rect(c, x_card, y_card, 4, card_h, COLOR_TEXT_MAIN)
        # Card Text
        pdf_text(c, x_card + 15, y_card + 15, t[card_key[0]], font_name="Arial-Bold", font_size=15, color=COLOR_TEXT_MAIN)
        pdf_text(c, x_card + 15, y_card + 45, t[card_key[1]], font_name="Arial", font_size=11, color=COLOR_TEXT_MUTED, max_w=card_w-25, line_height=1.3)
        
    c.showPage()
    
    # ----------------------------------------------------
    # SLIDE 4: Audience and Scale
    # ----------------------------------------------------
    pdf_rect(c, 0, 0, PDF_W, PDF_H, COLOR_BG)
    pdf_text(c, 80, 60, t['s4_title'], font_name="Arial-Bold", font_size=32, color=COLOR_TEXT_MAIN)
    
    # Left side cards
    card_w = 400
    card_h = 95
    y_start = 140
    gap_y = 15
    
    for idx, (lbl, text_key) in enumerate([('s4_b2b_title', 's4_b2b_text'), ('s4_b2c_title', 's4_b2c_text'), ('s4_b2g_title', 's4_b2g_text')]):
        curr_y = y_start + idx * (card_h + gap_y)
        pdf_rect(c, 80, curr_y, card_w, card_h, COLOR_CARD_BG, stroke_color=COLOR_BORDER, rx=4, ry=4)
        pdf_text(c, 95, curr_y + 15, t[lbl], font_name="Arial-Bold", font_size=15, color=COLOR_TEXT_MAIN)
        pdf_text(c, 95, curr_y + 40, t[text_key], font_name="Arial", font_size=11.5, color=COLOR_TEXT_MUTED, max_w=card_w - 30, line_height=1.3)
        
    # Target orientation below
    # Let's paint numbers or the whole string
    full_target = t['s4_target']
    # Highlight "90 000" or "90,000" in gold if found
    pdf_text(c, 80, 480, full_target, font_name="Arial", font_size=13.5, color=COLOR_TEXT_MUTED)
    
    # Right side image (GES-2 tunnel perspective)
    draw_pdf_image_fit(c, "scratch/extracted_img-011.png", 520, 0, 440, PDF_H)
    c.showPage()
    
    # ----------------------------------------------------
    # SLIDE 5: Scenario (Timeline)
    # ----------------------------------------------------
    pdf_rect(c, 0, 0, PDF_W, PDF_H, COLOR_BG)
    pdf_text(c, 80, 50, t['s5_title'], font_name="Arial-Bold", font_size=32, color=COLOR_TEXT_MAIN)
    
    # Central Timeline line
    timeline_x = PDF_W / 2
    pdf_line(c, timeline_x, 110, timeline_x, 430, stroke_color=COLOR_BORDER, border_w=2)
    
    step_y = [120, 200, 290, 380]
    steps_data = [
        ('s5_step1_time', 's5_step1_desc', 'left'),
        ('s5_step2_time', 's5_step2_desc', 'right'),
        ('s5_step3_time', 's5_step3_desc', 'left'),
        ('s5_step4_time', 's5_step4_desc', 'right')
    ]
    
    for idx, (time_key, desc_key, align) in enumerate(steps_data):
        cy = step_y[idx]
        # Draw central square number
        sq_size = 28
        pdf_rect(c, timeline_x - sq_size/2, cy, sq_size, sq_size, COLOR_CARD_BG, stroke_color=COLOR_BORDER, rx=3, ry=3)
        pdf_text(c, timeline_x, cy + 4, str(idx + 1), font_name="Arial-Bold", font_size=14, color=COLOR_TEXT_MAIN, align="center")
        
        # Draw text block
        text_w = 340
        if align == 'left':
            x_pos = timeline_x - 30
            # Time title
            pdf_text(c, x_pos, cy - 5, t[time_key], font_name="Arial-Bold", font_size=15, color=COLOR_TEXT_MAIN, align="right")
            # Desc text
            pdf_text(c, x_pos, cy + 18, t[desc_key], font_name="Arial", font_size=11, color=COLOR_TEXT_MUTED, align="right", max_w=text_w, line_height=1.3)
        else:
            x_pos = timeline_x + 30
            pdf_text(c, x_pos, cy - 5, t[time_key], font_name="Arial-Bold", font_size=15, color=COLOR_TEXT_MAIN, align="left")
            pdf_text(c, x_pos, cy + 18, t[desc_key], font_name="Arial", font_size=11, color=COLOR_TEXT_MUTED, align="left", max_w=text_w, line_height=1.3)
            
    # Throughput capacity below
    pdf_text(c, 80, 480, t['s5_throughput'], font_name="Arial", font_size=13.5, color=COLOR_TEXT_MUTED)
    c.showPage()
    
    # ----------------------------------------------------
    # SLIDE 6: Four principles
    # ----------------------------------------------------
    pdf_rect(c, 0, 0, PDF_W, PDF_H, COLOR_BG)
    pdf_text(c, 80, 60, t['s6_title'], font_name="Arial-Bold", font_size=32, color=COLOR_TEXT_MAIN)
    
    # Left column: principles
    pr_y = [140, 220, 310, 410]
    pr_data = [
        ('s6_p1_title', 's6_p1_desc'),
        ('s6_p2_title', 's6_p2_desc'),
        ('s6_p3_title', 's6_p3_desc'),
        ('s6_p4_title', 's6_p4_desc')
    ]
    
    for idx, (title_key, desc_key) in enumerate(pr_data):
        cy = pr_y[idx]
        pdf_text(c, 80, cy, t[title_key], font_name="Arial-Bold", font_size=17, color=COLOR_TEXT_MAIN)
        pdf_text(c, 80, cy + 24, t[desc_key], font_name="Arial", font_size=13, color=COLOR_TEXT_MUTED, max_w=420, line_height=1.3)
        
    # Right column: vertical arches photo
    draw_pdf_image_fit(c, "scratch/extracted_img-014.png", 550, 0, 410, PDF_H)
    c.showPage()
    
    # ----------------------------------------------------
    # SLIDE 7: Positioning (Table)
    # ----------------------------------------------------
    pdf_rect(c, 0, 0, PDF_W, PDF_H, COLOR_BG)
    pdf_text(c, 80, 50, t['s7_title'], font_name="Arial-Bold", font_size=32, color=COLOR_TEXT_MAIN)
    pdf_text(c, 80, 105, t['s7_sub'], font_name="Arial", font_size=14, color=COLOR_TEXT_MUTED)
    
    # Draw Table
    # Widths: Col 0: 140, Col 1: 200, Col 2: 200, Col 3: 240
    col_w = [150, 190, 190, 270]
    row_h = [40, 60, 60, 50, 70] # Header + 4 data rows
    y_tbl = 140
    
    headers = [t['s7_col0'], t['s7_col1'], t['s7_col2'], t['s7_col3']]
    rows_data = [
        [t['s7_r1_lbl'], t['s7_r1_val1'], t['s7_r1_val2'], t['s7_r1_val3']],
        [t['s7_r2_lbl'], t['s7_r2_val1'], t['s7_r2_val2'], t['s7_r2_val3']],
        [t['s7_r3_lbl'], t['s7_r3_val1'], t['s7_r3_val2'], t['s7_r3_val3']],
        [t['s7_r4_lbl'], t['s7_r4_val1'], t['s7_r4_val2'], t['s7_r4_val3']]
    ]
    
    # Draw Header Row
    curr_y = y_tbl
    x_offset = 80
    for c_idx, val in enumerate(headers):
        w = col_w[c_idx]
        # Draw background header block
        pdf_rect(c, x_offset, curr_y, w, row_h[0], COLOR_CARD_BG, stroke_color=COLOR_BORDER)
        pdf_text(c, x_offset + 10, curr_y + 12, val, font_name="Arial-Bold", font_size=12.5, color=COLOR_TEXT_MAIN)
        x_offset += w
        
    curr_y += row_h[0]
    
    # Draw Rows
    for r_idx, row in enumerate(rows_data):
        h = row_h[r_idx + 1]
        x_offset = 80
        
        # Background color alternating
        bg_color = COLOR_BG if r_idx % 2 == 0 else COLOR_CARD_BG
        
        for c_idx, val in enumerate(row):
            w = col_w[c_idx]
            pdf_rect(c, x_offset, curr_y, w, h, bg_color, stroke_color=COLOR_BORDER)
            
            # Formatting text
            is_neuro = (c_idx == 3) # Neurotunnel column
            font = "Arial-Bold" if is_neuro else "Arial"
            color = COLOR_TEXT_MAIN if is_neuro else COLOR_TEXT_MUTED
            size = 11.5 if is_neuro else 11
            
            pdf_text(c, x_offset + 10, curr_y + 12, val, font_name=font, font_size=size, color=color, max_w=w-20, line_height=1.3)
            x_offset += w
        curr_y += h
        
    c.showPage()
    
    # ----------------------------------------------------
    # SLIDE 8: Business model
    # ----------------------------------------------------
    pdf_rect(c, 0, 0, PDF_W, PDF_H, COLOR_BG)
    pdf_text(c, 80, 60, t['s8_title'], font_name="Arial-Bold", font_size=32, color=COLOR_TEXT_MAIN)
    
    # Top columns
    pdf_text(c, 80, 140, t['s8_h1'], font_name="Arial-Bold", font_size=18, color=COLOR_TEXT_MAIN)
    pdf_text(c, 80, 175, t['s8_t1'], font_name="Arial", font_size=13.5, color=COLOR_TEXT_MUTED, max_w=380, line_height=1.4)
    
    pdf_text(c, 500, 140, t['s8_h2'], font_name="Arial-Bold", font_size=18, color=COLOR_TEXT_MAIN)
    pdf_text(c, 500, 175, t['s8_t2'], font_name="Arial", font_size=13.5, color=COLOR_TEXT_MUTED, max_w=380, line_height=1.4)
    
    # Bottom cards
    card_w = 250
    card_h = 110
    gap = 25
    y_card = 340
    
    cards_data = [
        ('s8_c1_title', 's8_c1_desc'),
        ('s8_c2_title', 's8_c2_desc'),
        ('s8_c3_title', 's8_c3_desc')
    ]
    
    for idx, (title_key, desc_key) in enumerate(cards_data):
        x_card = 80 + idx * (card_w + gap)
        pdf_rect(c, x_card, y_card, card_w, card_h, COLOR_CARD_BG, stroke_color=COLOR_BORDER, rx=4, ry=4)
        pdf_rect(c, x_card, y_card, 4, card_h, COLOR_TEXT_MAIN)
        pdf_text(c, x_card + 15, y_card + 20, t[title_key], font_name="Arial-Bold", font_size=16, color=COLOR_TEXT_MAIN)
        
        # Highlight price in gold
        pdf_text(c, x_card + 15, y_card + 55, t[desc_key], font_name="Arial-Bold", font_size=13.5, color=COLOR_GOLD)
        
    c.showPage()
    
    # ----------------------------------------------------
    # SLIDE 9: Team and Partners
    # ----------------------------------------------------
    pdf_rect(c, 0, 0, PDF_W, PDF_H, COLOR_BG)
    pdf_text(c, 80, 50, t['s9_title'], font_name="Arial-Bold", font_size=32, color=COLOR_TEXT_MAIN)
    
    # Col 1: Alena
    x_col1 = 80
    y_col = 120
    pdf_text(c, x_col1, y_col, t['s9_a_name'], font_name="Arial-Bold", font_size=18, color=COLOR_TEXT_MAIN)
    # Scaled exact photo
    # Bounding box: width 230, height 290
    draw_pdf_image_fit(c, "images/alena_profile.png", x_col1, y_col + 30, 230, 220)
    pdf_text(c, x_col1, y_col + 265, t['s9_a_bio'], font_name="Arial", font_size=11, color=COLOR_TEXT_MUTED, max_w=230, line_height=1.35)
    
    # Col 2: Valery
    x_col2 = 360
    pdf_text(c, x_col2, y_col, t['s9_v_name'], font_name="Arial-Bold", font_size=18, color=COLOR_TEXT_MAIN)
    draw_pdf_image_fit(c, "images/valery_profile.png", x_col2, y_col + 30, 230, 220)
    pdf_text(c, x_col2, y_col + 265, t['s9_v_bio'], font_name="Arial", font_size=11, color=COLOR_TEXT_MUTED, max_w=230, line_height=1.35)
    
    # Col 3: Target Partners
    x_col3 = 640
    pdf_text(c, x_col3, y_col, t['s9_p_title'], font_name="Arial-Bold", font_size=18, color=COLOR_TEXT_MAIN)
    
    # Custom bullet rendering
    bullets = t['s9_p_list'].split('\n')
    y_bullet = y_col + 35
    for bullet in bullets:
        if bullet.strip():
            # Draw bullet circle or square
            pdf_rect(c, x_col3 + 2, y_bullet + 5, 4, 4, COLOR_GOLD, rx=2, ry=2)
            pdf_text(c, x_col3 + 15, y_bullet, bullet, font_name="Arial", font_size=14, color=COLOR_TEXT_MAIN)
            y_bullet += 25
            
    c.showPage()
    
    # ----------------------------------------------------
    # SLIDE 10: Roadmap & Status
    # ----------------------------------------------------
    pdf_rect(c, 0, 0, PDF_W, PDF_H, COLOR_BG)
    pdf_text(c, 80, 45, t['s10_title'], font_name="Arial-Bold", font_size=32, color=COLOR_TEXT_MAIN)
    
    # Central line timeline
    timeline_x = PDF_W / 2
    pdf_line(c, timeline_x, 100, timeline_x, 320, stroke_color=COLOR_BORDER, border_w=2)
    
    y_timeline = [105, 155, 215, 275]
    timeline_data = [
        ('s10_t1_date', 's10_t1_text', 'left'),
        ('s10_t2_date', 's10_t2_text', 'right'),
        ('s10_t3_date', 's10_t3_text', 'left'),
        ('s10_t4_date', 's10_t4_text', 'right')
    ]
    
    for idx, (date_key, text_key, align) in enumerate(timeline_data):
        cy = y_timeline[idx]
        # Bullet circle on the line
        bullet_r = 10
        pdf_rect(c, timeline_x - bullet_r/2, cy, bullet_r, bullet_r, COLOR_TEXT_MAIN, stroke_color=COLOR_TEXT_MAIN, rx=bullet_r/2, ry=bullet_r/2)
        
        text_w = 340
        if align == 'left':
            x_pos = timeline_x - 25
            pdf_text(c, x_pos, cy - 6, t[date_key], font_name="Arial-Bold", font_size=14, color=COLOR_TEXT_MAIN, align="right")
            pdf_text(c, x_pos, cy + 12, t[text_key], font_name="Arial", font_size=10.5, color=COLOR_TEXT_MUTED, align="right", max_w=text_w, line_height=1.3)
        else:
            x_pos = timeline_x + 25
            pdf_text(c, x_pos, cy - 6, t[date_key], font_name="Arial-Bold", font_size=14, color=COLOR_TEXT_MAIN, align="left")
            pdf_text(c, x_pos, cy + 12, t[text_key], font_name="Arial", font_size=10.5, color=COLOR_TEXT_MUTED, align="left", max_w=text_w, line_height=1.3)
            
    # Bottom Left: What we seek
    y_bottom = 350
    pdf_text(c, 80, y_bottom, t['s10_seek_title'], font_name="Arial-Bold", font_size=17, color=COLOR_TEXT_MAIN)
    
    seeking_items = [t['s10_seek1'], t['s10_seek2'], t['s10_seek3']]
    y_item = y_bottom + 25
    for item in seeking_items:
        pdf_rect(c, 82, y_item + 5, 4, 4, COLOR_GOLD, rx=2, ry=2)
        pdf_text(c, 95, y_item, item, font_name="Arial", font_size=12, color=COLOR_TEXT_MUTED)
        y_item += 22
        
    # Bottom Right: Target metrics box
    box_w = 390
    box_h = 135
    x_box = 490
    y_box = 350
    pdf_rect(c, x_box, y_box, box_w, box_h, "#334155", rx=5, ry=5)
    pdf_text(c, x_box + 20, y_box + 15, t['s10_target_title'], font_name="Arial-Bold", font_size=15, color="#FFFFFF")
    
    metric_y = y_box + 42
    for idx, item in enumerate(t['s10_targets']):
        val = item['val']
        lbl = item['lbl']
        # Compute string width of the value in gold
        c.saveState()
        c.setFont("Arial-Bold", 12.5)
        c.setFillColor(HexColor(COLOR_GOLD))
        y_draw = PDF_H - metric_y - 12.5 * 0.8
        c.drawString(x_box + 20, y_draw, val)
        val_w = c.stringWidth(val, "Arial-Bold", 12.5)
        c.restoreState()
        
        # Rest of text in white
        pdf_text(c, x_box + 20 + val_w, metric_y, lbl, font_name="Arial", font_size=12, color="#E2E8F0")
        metric_y += 24
        
    c.showPage()
    
    # ----------------------------------------------------
    # SLIDE 11: End
    # ----------------------------------------------------
    pdf_rect(c, 0, 0, PDF_W, PDF_H, COLOR_BG)
    pdf_text(c, PDF_W / 2, PDF_H / 2 - 15, t['s11_text'], font_name="Arial-Bold", font_size=28, color=COLOR_TEXT_MAIN, align="center")
    c.showPage()
    
    c.save()
    print(f"Presentation saved successfully to {filename}")

def main():
    if len(sys.argv) > 1:
        lang = sys.argv[1]
    else:
        lang = 'en'
        
    if lang not in ['ru', 'en']:
        print("Usage: python generate_pitch_light.py [ru|en]")
        sys.exit(1)
        
    filename = f"Neirotunnel_thestr_{lang.upper()}.pdf"
    draw_presentation(lang, filename)

if __name__ == "__main__":
    main()
