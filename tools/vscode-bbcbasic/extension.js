// tools/vscode-bbcbasic/extension.js
// JavaScript-Runtime fuer die BBC-BASIC-Extension.
//
// Registriert folgende Provider bei VS Code:
//
//   1. DefinitionProvider - Strg+Klick auf einen PROC_/FN_-Aufruf
//      springt zur passenden DEF-Zeile. Zuerst im aktuellen Dokument
//      gesucht, dann workspace-weit in allen *.bas-Dateien (ausser
//      sdcard/staged/, weil dort die auto-inlined Library-Kopie
//      liegt und Duplikate liefern wuerde).
//
//   2. DocumentSymbolProvider - fuellt den Outline-View und
//      Ctrl+Shift+O ("Go to Symbol in File") mit allen PROCs/FNs.
//
//   3. HoverProvider - Maus ueber eine VDU-/PLOT-/OSBYTE-Anweisung
//      zeigt eine erklaerende Tooltip inkl. Link auf die offizielle
//      Doku. Tabelle unten in DOC_PATTERNS erweiterbar.
//
// Kein npm, keine Dependencies - nur vscode-API plus Node-Builtins.
// Syntax-check lokal: `node --check extension.js`.

const vscode = require("vscode");

// Matcht `PROC_foo`, `PROCfoo`, `FN_bar`, `FNbar` - mit oder ohne
// Underscore zwischen Keyword und Namen.
const PROC_WORD_REGEX = /(?:PROC|FN)_?[A-Za-z][A-Za-z0-9_]*/;
// DEF-Zeilen finden wir mit diesem Pattern; gi-Flag fuer globales
// Mehrfach-Match und Case-Insensitivitaet.
const DEF_REGEX = /\bDEF\s+((?:PROC|FN)_?[A-Za-z][A-Za-z0-9_]*)\b/gi;

function escapeForRegex(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

async function findDefinitionInDocument(document, name) {
    const re = new RegExp(`\\bDEF\\s+${escapeForRegex(name)}\\b`, "i");
    const text = document.getText();
    const m = re.exec(text);
    if (!m) return null;
    const nameOffset = m.index + m[0].indexOf(name);
    return new vscode.Location(
        document.uri,
        document.positionAt(nameOffset)
    );
}

const definitionProvider = {
    async provideDefinition(document, position) {
        const range = document.getWordRangeAtPosition(position, PROC_WORD_REGEX);
        if (!range) return null;
        const word = document.getText(range);

        // 1) Zuerst im aktuellen Dokument
        const hit = await findDefinitionInDocument(document, word);
        if (hit) return hit;

        // 2) Sonst workspace-weit in allen *.bas (staged-Kopien ausnehmen)
        const files = await vscode.workspace.findFiles(
            "**/*.bas",
            "**/sdcard/staged/**"
        );
        for (const uri of files) {
            if (uri.toString() === document.uri.toString()) continue;
            const doc = await vscode.workspace.openTextDocument(uri);
            const found = await findDefinitionInDocument(doc, word);
            if (found) return found;
        }
        return null;
    },
};

const documentSymbolProvider = {
    provideDocumentSymbols(document) {
        const symbols = [];
        const text = document.getText();
        // lastIndex zuruecksetzen - das ist eine modul-weite RegExp
        DEF_REGEX.lastIndex = 0;
        let m;
        while ((m = DEF_REGEX.exec(text)) !== null) {
            const name = m[1];
            const kind = name.toUpperCase().startsWith("FN")
                ? vscode.SymbolKind.Function
                : vscode.SymbolKind.Method;
            const nameOffset = m.index + m[0].indexOf(name);
            const start = document.positionAt(nameOffset);
            const end = document.positionAt(nameOffset + name.length);
            const range = new vscode.Range(start, end);
            symbols.push(
                new vscode.DocumentSymbol(
                    name,
                    "BBC BASIC procedure",
                    kind,
                    range,
                    range
                )
            );
        }
        return symbols;
    },
};

// ============================================================
// HoverProvider - erklaert VDU / PLOT / *FX-Anweisungen
// ============================================================
//
// DOC_PATTERNS ist von SPEZIFISCH nach GENERISCH sortiert. Das erste
// Pattern, das auf den Statement-Bereich um den Cursor matcht, gewinnt.
// Die `match`-Regex soll die GESAMTE Anweisung erkennen (nicht nur das
// Schluesselwort), damit sie gegen das isolierte Statement gepruefft
// werden kann.

const DOC_BASE_URL = "https://agonplatform.github.io/agon-docs";

const DOC_PATTERNS = [
    // --- VDU 23, 27 Bitmap/Sprite ----------------------------------
    {
        match: /\bVDU\s*23\s*,\s*27\s*,\s*0\s*,/i,
        title: "VDU 23, 27, 0, n — Select Bitmap (8-bit ID)",
        body:
            "Waehlt das Bitmap mit der gegebenen 8-Bit-ID als **aktiv**. " +
            "Muss vor Load/Capture/Plot-Kommandos aufgerufen werden.\n\n" +
            "Bitmap-IDs 0..255 mappen intern auf Buffer 64000+n.\n\n" +
            "**Syntax:** `VDU 23, 27, 0, n`",
        doc: `${DOC_BASE_URL}/vdp/Bitmaps-API/`,
    },
    {
        match: /\bVDU\s*23\s*,\s*27\s*,\s*1\s*,/i,
        title: "VDU 23, 27, 1, w; h; data... — Bitmap-Daten laden",
        body:
            "Laedt `w*h*4` Bytes im **RGBA8888**-Format ins aktive Bitmap.\n\n" +
            "Vorher `VDU 23, 27, 0, n` aufrufen, um Ziel-Bitmap zu waehlen.\n\n" +
            "Typisches Muster (16x16):\n\n" +
            "```basic\n" +
            "VDU 23, 27, 0, 0\n" +
            "VDU 23, 27, 1, 16; 16;\n" +
            'f% = OPENIN "sprite.rgba"\n' +
            "FOR i% = 1 TO 1024 : VDU BGET#f% : NEXT\n" +
            "CLOSE#f%\n" +
            "```",
        doc: `${DOC_BASE_URL}/vdp/Bitmaps-API/`,
    },
    {
        match: /\bVDU\s*23\s*,\s*27\s*,\s*3\s*,/i,
        title: "VDU 23, 27, 3, x; y; — Bitmap zeichnen",
        body:
            "Zeichnet das aktive Bitmap an Pixel-Position (x, y). " +
            "Veraltet; seit VDP 2.2.0 empfohlen: `PLOT`-Kommando verwenden.\n\n" +
            "**Syntax:** `VDU 23, 27, 3, x; y;`",
        doc: `${DOC_BASE_URL}/vdp/Bitmaps-API/`,
    },
    {
        match: /\bVDU\s*23\s*,\s*27\s*,\s*4\s*,/i,
        title: "VDU 23, 27, 4, n — Select Sprite",
        body:
            "Waehlt Sprite `n` als aktiv. Alle folgenden Sprite-Kommandos " +
            "(Frame zuweisen, positionieren, zeigen, verstecken) beziehen " +
            "sich auf das aktive Sprite.\n\n" +
            "**Syntax:** `VDU 23, 27, 4, n`",
        doc: `${DOC_BASE_URL}/vdp/Bitmaps-API/`,
    },
    {
        match: /\bVDU\s*23\s*,\s*27\s*,\s*5\b/i,
        title: "VDU 23, 27, 5 — Sprite-Frames loeschen",
        body: "Entfernt alle Frames vom aktiven Sprite. Vor `VDU 23, 27, 6` ueblich.",
        doc: `${DOC_BASE_URL}/vdp/Bitmaps-API/`,
    },
    {
        match: /\bVDU\s*23\s*,\s*27\s*,\s*6\s*,/i,
        title: "VDU 23, 27, 6, n — Bitmap als Sprite-Frame",
        body:
            "Haengt Bitmap `n` als Frame an das aktive Sprite an. Mehrere " +
            "Frames hintereinander = Animation (per `VDU 23, 27, 8/9/10` " +
            "durchschalten).\n\n" +
            "**Syntax:** `VDU 23, 27, 6, bitmap_id`",
        doc: `${DOC_BASE_URL}/vdp/Bitmaps-API/`,
    },
    {
        match: /\bVDU\s*23\s*,\s*27\s*,\s*7\s*,/i,
        title: "VDU 23, 27, 7, N — Anzahl aktiver Sprites",
        body:
            "Setzt die Gesamtzahl der gleichzeitig darstellbaren Sprites (1..254). " +
            "Jedes weitere Sprite muss per `VDU 23, 27, 4, i` + Frame-Setup " +
            "vorbereitet sein.",
        doc: `${DOC_BASE_URL}/vdp/Bitmaps-API/`,
    },
    {
        match: /\bVDU\s*23\s*,\s*27\s*,\s*11\b/i,
        title: "VDU 23, 27, 11 — Sprite zeigen",
        body: "Blendet das aktive Sprite ein. Paar mit `VDU 23, 27, 12` (hide).",
        doc: `${DOC_BASE_URL}/vdp/Bitmaps-API/`,
    },
    {
        match: /\bVDU\s*23\s*,\s*27\s*,\s*12\b/i,
        title: "VDU 23, 27, 12 — Sprite verstecken",
        body: "Blendet das aktive Sprite aus. Gegenstueck zu `VDU 23, 27, 11`.",
        doc: `${DOC_BASE_URL}/vdp/Bitmaps-API/`,
    },
    {
        match: /\bVDU\s*23\s*,\s*27\s*,\s*13\s*,/i,
        title: "VDU 23, 27, 13, x; y; — Sprite positionieren",
        body:
            "Verschiebt das aktive Sprite an die **physischen** Pixel-" +
            "Koordinaten (x, y). In MODE 8 also 0..319 / 0..239 — **nicht** " +
            "die logischen 1280x1024 von MOVE/PLOT.\n\n" +
            "Nach dem Move unbedingt `VDU 23, 27, 15` aufrufen, sonst " +
            "bleibt die Aenderung unsichtbar.",
        doc: `${DOC_BASE_URL}/vdp/Bitmaps-API/`,
    },
    {
        match: /\bVDU\s*23\s*,\s*27\s*,\s*15\b/i,
        title: "VDU 23, 27, 15 — Sprites refreshen",
        body:
            "**Kritisch:** schreibt alle Sprite-Aenderungen (Position, " +
            "Show/Hide, Frame-Wechsel) ins sichtbare Bild. Ohne Refresh " +
            "bleiben die Aenderungen im Back-Buffer.",
        doc: `${DOC_BASE_URL}/vdp/Bitmaps-API/`,
    },
    {
        match: /\bVDU\s*23\s*,\s*27\s*,\s*16\b/i,
        title: "VDU 23, 27, 16 — Sprites & Bitmaps zuruecksetzen",
        body: "Loescht alle Sprites und Bitmaps. Hard-Reset, selten noetig.",
        doc: `${DOC_BASE_URL}/vdp/Bitmaps-API/`,
    },

    // --- VDU 23 (andere) -------------------------------------------
    {
        match: /\bVDU\s*23\s*,\s*1\s*,\s*0\b/i,
        title: "VDU 23, 1, 0 — Cursor aus",
        body: "Versteckt den blinkenden Text-Cursor. Typisch vor MODE-8-Grafik.",
        doc: `${DOC_BASE_URL}/vdp/VDU-Commands/`,
    },
    {
        match: /\bVDU\s*23\s*,\s*1\s*,\s*1\b/i,
        title: "VDU 23, 1, 1 — Cursor an",
        body: "Blendet den Text-Cursor wieder ein. Gegenstueck zu `VDU 23, 1, 0`.",
        doc: `${DOC_BASE_URL}/vdp/VDU-Commands/`,
    },

    // --- Top-Level VDU -------------------------------------------
    {
        match: /\b(?:VDU\s*22\s*,|MODE)\s*\d+/i,
        title: "MODE n / VDU 22, n — Bildschirmmodus",
        body:
            "Wechselt in Screen-Mode `n`. `MODE 8` entspricht `VDU 22, 8`. " +
            "Wichtige Modes:\n\n" +
            "| Mode | Aufloesung | Farben |\n" +
            "|------|------------|--------|\n" +
            "| 0    | 80x30 Text | 16     |\n" +
            "| 3    | 80x25 Text | 16     |\n" +
            "| 8    | 320x240    | 64     |\n" +
            "| 22   | 384x240    | 16     |\n",
        doc: `${DOC_BASE_URL}/vdp/Screen-Modes/`,
    },
    {
        match: /\b(?:VDU\s*25\s*,|PLOT)\s*\d+/i,
        title: "PLOT k / VDU 25, k, x; y; — Grafisches Zeichnen",
        body:
            "Grafik-Primitiv. `PLOT k, x, y` = `VDU 25, k, x; y;`. Haeufige " +
            "k-Codes:\n\n" +
            "| k    | Aktion                         |\n" +
            "|------|--------------------------------|\n" +
            "| 4    | MOVE absolut                   |\n" +
            "| 5    | DRAW absolut (Linie)           |\n" +
            "| 81   | Dreieck gefuellt               |\n" +
            "| 101  | Rechteck gefuellt (MOVE+PLOT)  |\n" +
            "| 157  | Kreis-Rand                     |\n" +
            "| 159  | Kreis gefuellt                 |\n",
        doc: `${DOC_BASE_URL}/vdp/PLOT-Commands/`,
    },
    {
        match: /\bGCOL\b\s*\d+/i,
        title: "GCOL mode, col — Grafikfarbe setzen",
        body:
            "Setzt die Grafikfarbe fuer nachfolgende MOVE/DRAW/PLOT-Kommandos.\n\n" +
            "**mode:** 0=plot, 1=OR, 2=AND, 3=XOR, 4=INV, 5=unchanged\n\n" +
            "**col:** Farbnummer 0..63 in MODE 8, 0..15 in 16-Farben-Modes",
        doc: `${DOC_BASE_URL}/vdp/VDU-Commands/`,
    },
    {
        match: /\bINKEY\s*\(\s*-\s*\d+\s*\)/i,
        title: "INKEY(-N) — Direkter Scancode-Scan",
        body:
            "Liefert TRUE wenn die Taste mit BBC-Micro-Scancode `N` aktuell " +
            "gedrueckt wird. Auf Agon/FabGL 1:1 gemappt. Wichtige Codes:\n\n" +
            "| Taste | N   |\n" +
            "|-------|-----|\n" +
            "| A     | 66  |\n" +
            "| D     | 51  |\n" +
            "| W     | 87  |\n" +
            "| S     | 82  |\n" +
            "| Space | 99  |\n" +
            "| ESC   | 113 |\n" +
            "| Left  | 26  |\n" +
            "| Right | 122 |\n" +
            "| Up    | 58  |\n" +
            "| Down  | 42  |\n\n" +
            "Vs. `INKEY(0)` = naechstes Zeichen aus Puffer (-1 wenn leer).",
        doc: "../docs/REFERENCE.md",
    },

    // --- OSBYTE / *FX --------------------------------------------
    {
        match: /\*FX\s*11\b/i,
        title: "*FX 11, n — Keyboard-Repeat Delay",
        body:
            "Setzt die Verzoegerung, bis eine gedrueckte Taste zu " +
            "wiederholen beginnt, auf `n * 10 ms` (Default 320 ms = 32). " +
            "Kleinerer Wert = schnellere erste Wiederholung.",
        doc: `${DOC_BASE_URL}/mos/Star-Commands/`,
    },
    {
        match: /\*FX\s*12\b/i,
        title: "*FX 12, n — Keyboard-Repeat Rate",
        body:
            "Setzt den Abstand zwischen automatischen Wiederholungen " +
            "auf `n * 10 ms` (Default 80 ms = 8). Kleinerer Wert = " +
            "schnellere Folge.",
        doc: `${DOC_BASE_URL}/mos/Star-Commands/`,
    },
    {
        match: /\*FX\s*19\b/i,
        title: "*FX 19 — auf VSync warten",
        body:
            "Blockiert bis zum naechsten Vertikal-Retrace (~16.67 ms " +
            "bei 60 Hz). **Das einzige OSBYTE-Kommando, das der Agon " +
            "versteht.** Essenziell fuer frame-rate-kontrollierte Loops.",
        doc: `${DOC_BASE_URL}/mos/Star-Commands/`,
    },
];

function statementAroundCursor(lineText, col) {
    // Extrahiert das Statement (getrennt durch ":") um die gegebene
    // Cursor-Spalte. Naiv, ignoriert `:` in Strings - reicht fuer
    // Hover-Tooltips.
    let start = 0;
    for (let i = col - 1; i >= 0; i--) {
        if (lineText[i] === ":") {
            start = i + 1;
            break;
        }
    }
    let end = lineText.length;
    for (let i = col; i < lineText.length; i++) {
        if (lineText[i] === ":") {
            end = i;
            break;
        }
    }
    return lineText.slice(start, end);
}

const hoverProvider = {
    provideHover(document, position) {
        const lineText = document.lineAt(position.line).text;
        const stmt = statementAroundCursor(lineText, position.character);
        if (!stmt.trim()) return null;

        for (const p of DOC_PATTERNS) {
            if (p.match.test(stmt)) {
                const md = new vscode.MarkdownString();
                md.isTrusted = false;
                md.supportHtml = false;
                md.appendMarkdown(`**${p.title}**\n\n${p.body}`);
                if (p.doc) {
                    md.appendMarkdown(`\n\n[Offizielle Doku](${p.doc})`);
                }
                return new vscode.Hover(md);
            }
        }
        return null;
    },
};

function activate(context) {
    context.subscriptions.push(
        vscode.languages.registerDefinitionProvider(
            "bbcbasic",
            definitionProvider
        ),
        vscode.languages.registerDocumentSymbolProvider(
            "bbcbasic",
            documentSymbolProvider
        ),
        vscode.languages.registerHoverProvider("bbcbasic", hoverProvider)
    );
}

function deactivate() {}

module.exports = { activate, deactivate };
