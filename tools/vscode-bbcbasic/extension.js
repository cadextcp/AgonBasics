// tools/vscode-bbcbasic/extension.js
// JavaScript-Runtime fuer die BBC-BASIC-Extension.
//
// Registriert zwei Provider bei VS Code:
//   1. DefinitionProvider - Strg+Klick auf einen PROC_/FN_-Aufruf
//      springt zur passenden DEF-Zeile. Zuerst im aktuellen Dokument
//      gesucht, dann workspace-weit in allen *.bas-Dateien (ausser
//      sdcard/staged/, weil dort die auto-inlined Library-Kopie
//      liegt und Duplikate liefern wuerde).
//
//   2. DocumentSymbolProvider - fuellt den Outline-View und
//      Ctrl+Shift+O ("Go to Symbol in File") mit allen PROCs/FNs.
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

function activate(context) {
    context.subscriptions.push(
        vscode.languages.registerDefinitionProvider(
            "bbcbasic",
            definitionProvider
        ),
        vscode.languages.registerDocumentSymbolProvider(
            "bbcbasic",
            documentSymbolProvider
        )
    );
}

function deactivate() {}

module.exports = { activate, deactivate };
