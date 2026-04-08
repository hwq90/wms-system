const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8080;
const WMS_FILE = path.join(__dirname, 'WMS系统', 'wms_v2.html');

const server = http.createServer((req, res) => {
    if (req.url === '/' || req.url === '/index.html') {
        fs.readFile(WMS_FILE, (err, data) => {
            if (err) {
                res.writeHead(500);
                res.end('Error loading WMS file');
            } else {
                res.writeHead(200, { 'Content-Type': 'text/html' });
                res.end(data);
            }
        });
    } else {
        res.writeHead(404);
        res.end('Not found');
    }
});

server.listen(PORT, () => {
    console.log(`WMS Server running at http://localhost:${PORT}`);
    console.log(`Serving: ${WMS_FILE}`);
});