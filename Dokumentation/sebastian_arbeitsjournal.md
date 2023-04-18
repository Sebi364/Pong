# Arbeitsjournal von Sebastian
## 25/26.03.2023
Während des Wochenendes hab ich nochmals am Client getüftelt.
Neu wird der gesamte "Skin" vom Client in einem Ordner gespeichert und von einem .json config File beschrieben.
```json
{
    "name":"Gate",
    "field":{
        "pos":[80, 80],
        "width":1720,
        "height":880,
        "decal":"background.png",
        "type":"horizontal"
    },
    "player1":{
        "pos1":[0, 80],
        "pos2":[0, 820],
        "decal":"paddle.png"
    },
    "player2":{
        "pos1":[1840, 80],
        "pos2":[1840, 820],
        "decal":"paddle.png"
    },
    "ball":{
        "decal":"ball.png"
    },
    "score":{
        "pos":[960, 40],
        "font_size":80,
        "color":"Black",
        "font":"font.ttf"
    }
}
```

Das wird es demjenigen, der ein neues Theme entwirft ganz einfach ermöglichen viele Optionen zu ändern ohne in den Python code eintauchen zu müssen

Ein weiter plus Punkt von diesem weg ist, dass es möglich ist den Client so zu gestalten wie man will, der Designer ist nicht an die Dimensionen von den einzelnen Komponenten gebunden.

---
## 29.03.2023
Ich habe mich dazu entschieden den Server teil meines Programmes neu zu schreiben, die wichtigsten gründe für diese Entscheidung sind:
- Der Code wurde ein bisschen unleserlich

- Als ich den Server angefangen habe zu schreiben, wusste ich noch nicht genau wie alles funktionieren wird -> Im alten Server gibt es einige unnötige Teile.

- Beim alten Server gab es keinen "sinnvollen" weg um alte Spieler zu löschen, was zu unerwünschten Fehlverhalten führen konnte.

    - z. B.: Client1 verlässt während Warteschlange -> nächster Client der die Warteschlange betritt wird mit dem "totem" Client1 in ein Match getan.

    - Dieses Verhalten ist eine Konsequenz davon, dass ich solche Sachen nicht von Anfang an berücksichtigt habe. (weil ich es noch nicht wusste)

---
## 31.03.2023
Ich habe heute den neuen Server zum laufen gebracht.

---
## 02.04.2023
Heute hab ich die Funktion zum Spiel hinzugefügt das er nach einer gewissen Anzahl an Punkten das Spiel beendet. (sehr wichtiges feature) Der Vorteil davon liegt darin, dass eine runde nicht unendlich lange geht.

---
## 04.04.2023
Heute ist uns beim testen ein problem mit der zeit-synchronization aufgefallen. Das Problem besteht darin dass wen die Zeit auf einem Client, nicht gleich wie auf dem server ist, einige komponente (z.B. timer) falsche sachen anzeigen. Ich habe das problem vermindert in dem ich am anfang die Zeit des Servers an den Client schicke, dieser rechnet dann die diferenz aus und rechnet sie bei allen nötigen stellen hinzu. Dieser Weg ist zwar nicht Perfekt, aber gut genug für unseren Zweck.

Das problem ist mir bis jetzt nich aufgefallen weil der server und client meistens über den localhost getestet wurde. -> gleicher computer -> gleiche Zeit

---
## 05.04.2023
Heute habe ich den teil vom code geschrieben der Music / Sounds abspielen kann.

---
## 06.04.2023
Heute war ich mit einigen kleineren sachen beschäftigt:
- Loading screen
- Der spieler kann sich wärend einer Pause nicht mehr bewegen.

---
## 11.04.2023
Heute war ich mit der doku beschäftigt, und habe zum client ein feature hinzugefügt, dass es ihm erlaub zwischen zwei positionen vom ball zu interpollieren. Das ist ein sehr einfacher aber guter trick der die bewegungen vom ball viel flüssiger darstellt als sie es sind. Ich habe das programm getestet indem ich auf dem server die update-rate auf 10x pro sekunde beschränkt habe, was nicht für eine flüssige bewegung reicht. Ich bin selber überascht wie gut das funktioniert.

---
## 12.04.2023
Heute hab ich die interpolation verbessert indem ich sie auch beim Spieler eingesetzt habe.

---