const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname);
const PORT = Number(process.env.PORT || 5500);
const TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon"
};

http.createServer((request, response) => {
    let pathname;

    try {
        pathname = decodeURIComponent(new URL(request.url, "http://localhost").pathname);
    } catch {
        response.writeHead(400);
        response.end("Bad request");
        return;
    }

    if (pathname === "/") {
        pathname = "/pages/index.html";
    }

    let filePath = path.resolve(ROOT, `.${pathname}`);

    // Links emitidos antes do ajuste do FRONTEND_URL podem não ter /pages/.
    if (
        !pathname.startsWith("/pages/") &&
        path.extname(pathname).toLowerCase() === ".html"
    ) {
        const pageFallback = path.resolve(ROOT, "pages", path.basename(pathname));
        if (pageFallback.startsWith(path.resolve(ROOT, "pages") + path.sep)) {
            filePath = pageFallback;
        }
    }

    if (filePath !== ROOT && !filePath.startsWith(ROOT + path.sep)) {
        response.writeHead(403);
        response.end("Forbidden");
        return;
    }

    fs.readFile(filePath, (error, content) => {
        if (error) {
            response.writeHead(error.code === "ENOENT" ? 404 : 500, {
                "Content-Type": "text/plain; charset=utf-8"
            });
            response.end(error.code === "ENOENT" ? "Not found" : "Server error");
            return;
        }

        response.writeHead(200, {
            "Content-Type": TYPES[path.extname(filePath).toLowerCase()] || "application/octet-stream",
            "X-Content-Type-Options": "nosniff"
        });
        response.end(content);
    });
}).listen(PORT, "127.0.0.1", () => {
    console.log(`Frontend disponível em http://127.0.0.1:${PORT}/`);
});
