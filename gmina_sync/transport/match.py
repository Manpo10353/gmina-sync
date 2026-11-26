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


def stop_direction(direction_pdf):
    """Direction is 'Częstochowa' if the PDF says so, otherwise 'Rędziny'."""
    return "Częstochowa" if "CZĘSTOCHOWA" in direction_pdf.upper() else "Rędziny"


def match_stops(header, db_direction, stops):
    """Return a list of database stops matching a PDF header """
    direction = db_direction.upper()
    header = header.upper()
    if header in ALIASY:
        loc, name = ALIASY[header]
        return [s for s in stops
                if s["loc"].upper() == loc.upper()
                and s["name"].upper() == name.upper()
                and s["dir"].upper() == direction]
    return [s for s in stops
            if s["dir"].upper() == direction
            and header in ((s["loc"] + " " + s["name"]).upper(), s["name"].upper())]
