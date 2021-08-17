# **Nachti's Game 'Heist'**

Ein Überfall-Spiel (Heist) für den **[Streamlabs-Chatbot](https://streamlabs.com/chatbot?l=de-DE)**. Das Skript ersetzt das im **Streamlabs-Chatbot** unter '***Minigames***' eingebaute Spiel . Ich wollte mehr Konfigurations-Möglichkeiten, als es der **Streamlabs-Chatbot** selbst zulässt. Das vorliegende Skript kann mit mehreren Texten und Zielen gefüttert werden und zeigt diese dann zufällig an.

In der Grundkonfiguration habe ich Ziele und Texte mit Bezug aus dem ***Shadowrun***-*Universum* verwendet. Die hierfür notwendigen Datenbank-Dateien und die von mir vorgesehenen Texte werden beim Import des Skriptes in den **Streamlabs-Chatbot** erstellt.


## **Eigene Text-Ausgaben**

Die Textausgaben im Chat sind innerhalb der SQLite-Datenbank '***Games.db***' in der Tabelle '***game_heist_messages***' gespeichert. Die Datenbank-Datei findest du ausserhalb des Skript-Verzeichnis innerhalb des Verzeichnisses '*Skript*' deines Chatbots im Unter-Verzeichnis '***\_NACHTIS_DATABASE_FILES\_***'. Du kannst das Verzeichnis im Explorer durch die Verwendung der Schaltfläche innerhalb der Einstellungen öffnen. Die vorkonfigurierten Nachrichten können durch die Schaltfläche '***Benachrichtigungen zurücksetzen***' innerhalb der Einstellungen wieder hergestellt werden.


### ***Textausgaben im Chat nach Nachrichten-Typ***

Die möglichen Nachrichten-Typen (*messageType*) und die möglichen Variablen lauten:


- **IsOnCoolDown** *(Spiel befindet sich aktuell in der eingestellten Cooldown-Phase)*
        
        {time}          = Cooldown Zeit
        {command}       = Kommando des Spiels


- **GameCooldownOver** *(Cooldown ist abgelaufen [Zeitgesteuererter Text])*
        
        {command}       = Kommando des Spiels


- **NewGameStart** *(Start Benachrichtigung für den ersten Teilnehmer, der am Spiel teilnimmt)*

        {user}          = Name des Users, der den Heist gestartet hat
        {command}       = Kommando des Spiels
        {target}        = Name des Ziels
        {time}          = Zeit bis das Spiel startet
        {maxpoints}     = Höhe des maximalen Einsatzes
        {pointsname}    = Name der Chatbot-Punkte


- **NewPlayer** *(Anzeige des Textes bei jedem weiteren Teilnehmer)*

        {user}          = Name des Users, der am Heist teilnimmt
        {target}        = Name des Ziels
        {stake}         = Einsatz des Spielers
        {pointsname}    = Name der Chatbot-Punkte


- **NotEnoughPlayer** *(Es haben sich nicht genügend Spieler zur Teilnahme angemeldet)*

        {target}        = Name des Ziels
        {pointsname}    = Name der Chatbot-Punkte


- **GameStartIntro** *(Erster Text, der beim Spielstart angezeigt wird)*

        {target}        = Name des Ziels


- **Outcome_100Percent** *(Ausgabetext, wenn alle Spieler überlebt haben)*

        {target}        = Name des Ziels


- **Outcome_75_99Percent** *(Ausgabetext, wenn 75-99% der Spieler überlebt haben)*
        
        {target}        = Name des Ziels


- **Outcome_25_74Percent** *(Ausgabetext, wenn 25-74% der Spieler überlebt haben)*
    
        {target}        = Name des Ziels


- **Outcome_01_24Percent** *(Ausgabetext, wenn 1-24% der Spieler überlebt haben)*
    
        {target}        = Name des Ziels


- **Outcome_00Percent** *(Ausgabetext, wenn keiner der Spieler überlebt hat)*
    
        {target}        = Name des Ziels


- **NotEnoughPoints** *(Spieler hat nicht genug Punkte)*

        {user}          = Name des Spielers
        {target}        = Name des Ziels
        {points}        = Punkte des Spielers
        {pointsname}    = Name der Chatbot-Punkte


- **StakeBelowMinimum** *(Einsatz ist unterhalb des eingestellten Minimalbetrags)*

        {user}          = Name des Spielers
        {minpoints}     = Höhe des maximalen Einsatzes
        {pointsname}    = Name der Chatbot-Punkte


- **StakeOverMaximum** *(Einsatz ist grösser als der eingestellte Maximalbetrag)*

        {user}          = Name des Spielers
        {target}        = Name des Ziels
        {command}       = Kommando zum Aufruf des Spieles
        {maxpoints}     = Höhe des maximalen Einsatzes
        {pointsname}    = Name der Chatbot-Punkte


- **WrongCommandOption** *(Falscher Kommandoaufruf)*

        {user}          = Name des Spielers
        {command}       = Kommando zum Aufruf des Spieles
        {maxpoints}     = Höhe des maximalen Einsatzes
        {pointsname}    = Name der Chatbot-Punkte



*Sollten sich mehrere Einträge mit der selben Nachrichten-Typen (*messageType*) Bezeichnung in der Tabelle '***game_heist_messages***' befinden, so wird zufällig eine der Nachrichten-Texte ausgewählt.*


## **Eigene Ziele**

Die Textausgaben im Chat sind innerhalb der SQLite-Datenbank '***Games.db***' in der Tabelle '***game_heist_targets***' gespeichert. Die Datenbank-Datei findest du ausserhalb des Skript-Verzeichnis innerhalb des Verzeichnisses '*Skript*' deines Chatbots im Unter-Verzeichnis '***\_NACHTIS_DATABASE_FILES\_***'. Du kannst das Verzeichnis im Explorer durch die Verwendung der Schaltfläche innerhalb der Einstellungen öffnen. Die vorkonfigurierten Nachrichten können durch die Schaltfläche '*Namen der Ziele zurücksetzen*' innerhalb der Einstellungen wieder hergestellt werden.

*Sollten sich mehrere Einträge in der Tabelle '****game_heist_targets****' befinden, so wird zufällig eine der Nachrichten-Texte ausgewählt.*


## **Hinweis**

### ***Verwendung der*** **Reset** ***-Funktion***

Die Einträge in der Datenbank können durch die Verwendung der entsprechenden Buttons auf definierte Werte zurück gesetzt werden. Diese Buttons findest du in den Einstellungen des Skriptes unter dem Punkt '***Skript Reset***'. Beachte, dass mit dem Klick auf einen der Button alle vorherigen Einträge gelöscht und durch die Default-Werte ersetzt werden. 

**Dieser Vorgang kann nicht Rückgängig gemacht werden.** 

Eine Sicherheitsabfrage warnt dich, bevor die Daten entgültig gelöscht werden.


## **Empfohlene Tools**

Um die Datenbank-Einträge bearbeiten zu können verwende am Besten den '***DB Browser for SQLite***'. Das Programm kannst du auf der Seite **[sqlitebrowser.org](https://sqlitebrowser.org/)** kostenlos herunterladen.