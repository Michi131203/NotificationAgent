# Notification Agent

Der Notification Agent ist ein automatisierter Dienst zur Erstellung personalisierter Event-Benachrichtigungen für App-Nutzer.

## Funktionsweise

Jeden Sonntag um **09:00 Uhr** wird der Agent automatisch ausgeführt und durchläuft mehrere Verarbeitungsschritte:

### 1. Datenbank-Cleanup

Zu Beginn werden veraltete Event-Datensätze bereinigt. Alle Events, deren Datum länger als einen Monat zurückliegt, werden aus der Datenbank entfernt.

### 2. Datenaggregation

Anschließend werden die relevanten Daten für die Benachrichtigungserstellung geladen:

* Nutzer und deren favorisierte Kategorien aus der Tabelle `user_categories`
* Aktuelle und relevante Events aus der Event-Datenbank
* Weitere notwendige Metadaten zur Personalisierung

### 3. Analyse & Personalisierung

Der Agent analysiert die verfügbaren Events und gleicht diese mit den favorisierten Kategorien der jeweiligen Nutzer ab. Dabei werden ausschließlich relevante und aktuelle Veranstaltungen berücksichtigt. Durch diesen Filterprozess wird für jeden Nutzer eine individuelle Auswahl passender Events ermittelt.

### 4. KI-gestützte Nachrichtengenerierung

Die gefilterten und aufbereiteten Event-Daten werden an die Claude API übermittelt. Auf Basis der Nutzerinteressen und der ausgewählten Veranstaltungen erstellt die KI eine natürlich formulierte und personalisierte Benachrichtigung. Ziel ist es, dem Nutzer die für ihn relevantesten Events in einer ansprechenden und leicht verständlichen Nachricht zusammenzufassen.

### 5. Speicherung der Benachrichtigungen

Die generierten Nachrichten werden in der Datenbank gespeichert und stehen anschließend für den Versand durch die Hauptanwendung bereit.

### 6. Logging & Monitoring

Während des gesamten Prozesses werden Log-Dateien erstellt, um folgende Informationen nachvollziehbar zu dokumentieren:

* Start- und Endzeit der Verarbeitung
* Anzahl bereinigter Events
* Anzahl analysierter Nutzer
* Anzahl generierter Benachrichtigungen
* Fehler und Ausnahmen während der Verarbeitung
* API-Aufrufe und Verarbeitungsstatus

### 7. Versand durch die App

Die Hauptanwendung liest die generierten Benachrichtigungen aus der Datenbank aus und versendet diese anschließend an die entsprechenden Nutzer.

## Workflow

1. Scheduler startet den Agenten jeden Sonntag um 09:00 Uhr.
2. Alte Events werden aus der Datenbank entfernt.
3. Nutzerpräferenzen und aktuelle Events werden geladen.
4. Relevante Events werden den Nutzern zugeordnet.
5. Claude API erstellt personalisierte Nachrichten aus den gefilterten Ergebnissen.
6. Nachrichten werden in der Datenbank gespeichert.
7. Logs werden erstellt und gespeichert.
8. Die App versendet die fertigen Benachrichtigungen an die Nutzer.
