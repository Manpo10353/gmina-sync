import re
import pdfplumber

DAY_COLS = ["workday_school", "saturday", "sunday_holiday", "workday_summer"]
TOKEN = re.compile(r"(\d{2})\s*([A-Za-z\-]*\*?)")

def parse_cell(text):
    return TOKEN.findall(text.replace("\n", " "))


def parse_pdf(path):
    rows = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            m_stop = re.search(r"Przystanek:\s*([^\n]+)", text)
            m_dir = re.search(r"Kierunek:\s*([^\n]+)", text)
            stop = m_stop.group(1).split("www.")[0].strip() if m_stop else ""
            direction = m_dir.group(1).split("www.")[0].strip() if m_dir else ""
            for table in page.extract_tables():
                for row in table:
                    if not row or not row[0] or not row[0].strip().isdigit():
                        continue
                    hour = int(row[0].strip())
                    for col, cell in enumerate(row[1:5]):
                        if not cell:
                            continue
                        for minute, code in parse_cell(cell):                            rows.append({
                                "przystanek": stop,
                                "kierunek": direction,
                                "day_type": DAY_COLS[col],
                                "godzina": f"{hour:02d}:{int(minute):02d}",
                                "kod": code,
                            })
    return rows
