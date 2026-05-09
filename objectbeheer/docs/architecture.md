# Architectuur

Deze applicatie is single-company per installatie.

Dat betekent dat elk bedrijf een eigen installatie, eigen database, eigen media en eigen instellingen krijgt.

Er is bewust geen multi-tenant laag met meerdere bedrijven in één database. Dat maakt de eerste versie eenvoudiger, veiliger en makkelijker te kopiëren.
