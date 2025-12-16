# Viral Barber Game Art Generator

Deze repository bevat een Python script dat drie concept-art screenshots genereert voor een "Viral Barber Game" (cel-shaded / arcade stijl).

Bestanden
- generate_barber_game.py  -- Het script dat de afbeeldingen maakt.
- output/                  -- Wordt aangemaakt door het script en bevat gameplay1.png, gameplay2.png en menu.png.

Installatie
1. Zorg dat je Python 3.8+ (bij voorkeur 3.11+) hebt.
2. Installeer dependencies:

   pip install --upgrade pillow numpy

Gebruik

   python generate_barber_game.py

Na uitvoeren: bekijk de gegenereerde afbeeldingen in de map "output".

Beschrijving van de gegenereerde beelden
- gameplay1.png: "The Precision Cut"
  - First-person POV, spelershand houdt een gouden tondeuse.
  - Blauwe vonken en combo-effecten, "PERFECT FADE!" centrale tekst.
  - Time Limit balk boven, verticale precisiemeter aan de zijkant.

- gameplay2.png: "The Street Brawl"
  - Side-scrolling 2D vechtscène met twee kappers-karakters.
  - Neon achtergrondbord: "IT'S A CUT-THROAT BUSINESS".
  - UI: health bars, timer 99, volle Super Meter.

- menu.png:
  - Split-screen menu: PRECISION CUT vs STREET BRAWL.
  - Icons: gekruiste gouden schaar/tondeuse en een vlammende vuist.
  - Vier character concept portretten in arcade-stijl.

Aanpassingen
- Je kunt de resolutie aanpassen door WIDTH/HEIGHT in het script te wijzigen.
- Voor betere typografie kun je een TTF font pad opgeven in FONT_PATH binnen het script.

Opmerkingen
- Dit script genereert gestileerde, programatisch gemaakte conceptbeelden (niet fotorealistisch). Het gebruikt moderne Pillow-functies en numpy voor kleine particle-effecten.
- Als je de afbeeldingen als referentie voor illustratoren of als mockups wilt gebruiken, kun je de output nader bewerken in een grafisch programma.

Veel plezier en succes met je project!