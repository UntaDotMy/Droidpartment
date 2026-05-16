// Audit unused identifiers in install.js
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const requires = [...src.matchAll(/^const\s+(\w+|\{[^}]+\})\s*=\s*require\(['"]([^'"]+)['"]\)/gm)];
for (const r of requires) {
    const ids = r[1].replace(/[{}]/g, '').split(',').map(s => s.trim());
    for (const id of ids) {
        const occurrences = src.match(new RegExp('\\b' + id + '\\b', 'g'));
        if (occurrences && occurrences.length <= 1) {
            console.log('  potentially unused require:', id);
        }
    }
}
const fnDecls = [...src.matchAll(/^(?:async\s+)?function\s+(\w+)/gm)];
for (const m of fnDecls) {
    const name = m[1];
    if (name === 'main') continue;
    const occurrences = src.match(new RegExp('\\b' + name + '\\b', 'g'));
    if (occurrences && occurrences.length <= 1) {
        console.log('  potentially unused function:', name);
    }
}
const constDecls = [...src.matchAll(/^const\s+(EXIT_\w+|[A-Z_]+)\s*=/gm)];
for (const m of constDecls) {
    const name = m[1];
    const occurrences = src.match(new RegExp('\\b' + name + '\\b', 'g'));
    if (occurrences && occurrences.length <= 1) {
        console.log('  potentially unused const:', name);
    }
}
