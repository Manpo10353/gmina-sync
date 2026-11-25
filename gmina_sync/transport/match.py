ALIASY = {
    "CZĘSTOCHOWA TENISOWA": ("Częstochowa", "Strefa"),
    "MARIANKA RĘDZIŃSKA": ("Marianka Rędzińska", "Marianka"),
    "MARIANKA RĘDZIŃSKA I": ("Marianka Rędzińska", "Marianka I"),
    "MARIANKA RĘDZIŃSKA II": ("Marianka Rędzińska", "Marianka II"),
    "RUDNIKI NOWE I": ("Rudniki", "Nowe 1"),
    "RUDNIKI NOWE II": ("Rudniki", "Nowe 2"),
    "RUDNIKI NOWE III": ("Rudniki", "Nowe 3"),
    "KAROLINA I": ("Karolina", "Karolina 1"),
    "RĘDZINY WOLNOŚCI (GÓRKA)": ("Rędziny", "Górka"),
    "RĘDZINY OSIEDLE (UL. WESOŁA)": ("Rędziny", "Osiedle ul.Wesoła"),
    "RĘDZINY UL. WESOŁA": ("Rędziny", "Wesoła"),
    "CZĘSTOCHOWA PL. DASZYŃSKIEGO": ("Częstochowa", "Plac Daszyńskiego"),
    "LATOSÓWKA SPACEROWA": ("Konin", "Latosówka Spacerowa"),
}


def kierunek_slupka(kierunek_pdf):
    """Direction is 'Częstochowa' if the PDF says so, otherwise 'Rędziny'."""
    return "Częstochowa" if "CZĘSTOCHOWA" in kierunek_pdf.upper() else "Rędziny"


def dopasuj(naglowek, kier_bazy, stops):
    """Return a list of database stops matching a PDF header """
    kier = kier_bazy.upper()
    naglowek = naglowek.upper()
    if naglowek in ALIASY:
        loc, nazwa = ALIASY[naglowek]
        return [s for s in stops
                if s["loc"].upper() == loc.upper()
                and s["name"].upper() == nazwa.upper()
                and s["dir"].upper() == kier]
    return [s for s in stops
            if s["dir"].upper() == kier
            and naglowek in ((s["loc"] + " " + s["name"]).upper(), s["name"].upper())]
