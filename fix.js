const fs = require('fs');
const path = require('path');
const installFile = path.join(__dirname, 'bin', 'install.js');
let content = fs.readFileSync(installFile, 'utf8');
content = content.replace('const matches = content.match(/^- id:/gm);', 'const matches = content.match(/- id:/gm);');
fs.writeFileSync(installFile, content);
console.log('Fixed countYamlEntries regex');
