# Security

Secrets staan in `.env` en niet in Git.

In productie moet DEBUG op False.

In productie moet HTTPS gebruikt worden.

Gebruikersrechten worden niet alleen in templates gecontroleerd.

Voorraadmutaties worden historisch opgeslagen en niet als simpel voorraadgetal overschreven.

Belangrijke verwijderacties moeten later via archiveren lopen in plaats van hard delete.
