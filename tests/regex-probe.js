// Diagnose isOurHookEntry regex
const cases = [
    '"C:/x/dpt.exe" hook pre-tool-use',
    '"/usr/local/bin/dpt" hook session-start',
    'dpt hook stop',
    'python /home/user/.factory/memory/hooks/hook-session-start.py',
    '/usr/local/bin/notify.sh',
    'echo unrelated_kept',
];

const oldRegex = /\bdpt(\.exe)?\b\s+hook\s/i;
const newRegex = /\bdpt(\.exe)?\b[^\w]+hook\b/i;
const altRegex = /(^|[\s"'/\\])dpt(\.exe)?[\s"']+hook\b/i;

for (const c of cases) {
    console.log('input:', JSON.stringify(c));
    console.log('  old:', oldRegex.test(c), '  new:', newRegex.test(c), '  alt:', altRegex.test(c));
}
