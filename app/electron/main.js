const { spawn } = require("child_process");
const path = require("path");
const { app, BrowserWindow, ipcMain, dialog } = require("electron");
const fs = require("fs");

let mainWindow;
let currentParser = null;
let cancelledByUser = false;
let hasSignaledDone = false;

// helper to resolve the Bokeh exe path
function getBokehExePath() {

    // When running from source (npm start)
    if (!app.isPackaged) {
        return path.join(__dirname, "../bokeh_app/bokeh_app.exe");
    }

    // When running from the installed app (electron-builder)
    return path.join(process.resourcesPath, "bokeh_app.exe");
}

// helper to resolve database path
function getDataPaths() {
    const base = path.join(app.getPath("userData"), "SlippiDV");
    if (!fs.existsSync(base)) fs.mkdirSync(base, { recursive: true });

    return {
        base,
        dbPath: path.join(base, "SlippiDV_FullData.json"),
        rejectedPath: path.join(base, "rejected_files.txt"),
        lastParsePath: path.join(base, "last_parse.txt"),
    };
}

const lastParseFile = path.join(__dirname, "../user_data/last_parse.txt");

// helper to resolve the Bokeh exe path
function getBokehExePath() {

    // When running from source (npm start)
    if (!app.isPackaged) {
        return path.join(__dirname, "../bokeh_app/bokeh_app.exe");
    }

    // When running from the installed app (electron-builder)
    return path.join(process.resourcesPath, "bokeh_app.exe");
}


function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1000,
        height: 700,
        webPreferences: {
            preload: path.join(__dirname, "preload.js"),
            contextIsolation: true,
            nodeIntegration: false
        }
    });

    mainWindow.loadFile("index.html");

    mainWindow.webContents.on("did-finish-load", () => {
        if (fs.existsSync(lastParseFile)) {
            const date = fs.readFileSync(lastParseFile, "utf8");
            console.log("Last parse date from file:", date);

            mainWindow.webContents.send("parser-event", {
                type: "last-parse",
                value: date
            });
        }
    });
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
    if (process.platform !== "darwin") app.quit();
});


//File Select Button
ipcMain.handle("select-folder", async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ["openDirectory"]
    });

    if (result.canceled) return null;

    return result.filePaths[0];
});

//Cancel Parser Action

ipcMain.on("cancel-parser", () => {
    if (currentParser && !currentParser.killed) {
        currentParser.kill("SIGTERM");
        mainWindow.webContents.send("parser-event", {
            type: "log",
            message: "Parse cancelled by user.\n"
        });
        mainWindow.webContents.send("parser-event", {
            type: "cancelled"
        });
        currentParser = null;
    }
});




//Run Parser Action
ipcMain.on("run-parser", (_, { slippiFolderPath, slippiID }) => {
    const parserDir = path.join(__dirname, "../parser");
    const parserPath = path.join(parserDir, "main.js");

    console.log("Launching parser with:", parserPath, slippiFolderPath, slippiID);

    // If a previous parser is still running, ignore or kill it first
    if (currentParser && !currentParser.killed) {
        currentParser.kill("SIGTERM");
    }

    // Cancel/Done Status update
    cancelledByUser = false;
    hasSignaledDone = false;

    const parser = spawn(
        process.execPath, // Electron's embedded Node
        [parserPath, slippiFolderPath, slippiID],
        { cwd: parserDir, stdio: ["ignore", "pipe", "pipe"] }
    );

    currentParser = parser;

    // Proper buffered stdout handling
    let buffer = "";

    parser.stdout.on("data", (data) => {
        buffer += data.toString();

        let lines = buffer.split("\n");
        buffer = lines.pop(); // keep partial line

        for (const line of lines) {
            if (!line.trim()) continue;

            if (line.startsWith("__PROGRESS__")) {
                // This is a structured progress event
                const json = line.slice("__PROGRESS__".length);

                try {
                    const { value, done, total } = JSON.parse(json);
                    mainWindow.webContents.send("parser-event", {
                        type: "progress",
                        value,
                        done,
                        total,
                    });
                } catch (err) {
                    console.error("Failed to parse progress JSON:", err);
                }
            } else if (line === "__DONE__") {
                // Trying to signal that the parser is done xDxD
                hasSignaledDone = true;
                mainWindow.webContents.send("parser-event", {
                    type: "done",
                });
                const now = new Date();
                fs.writeFileSync(lastParseFile, now.toLocaleString());
            } else {
                // Plain log line
                mainWindow.webContents.send("parser-event", {
                    type: "log",
                    message: line,
                });
            }
        }
    });

    parser.stderr.on("data", (data) => {
        const msg = data.toString();
        console.error("PARSER STDERR:", msg);
        mainWindow.webContents.send("parser-event", {
            type: "log",
            message: msg
        });
    });

    parser.on("error", (err) => {
        console.error("Failed to start parser:", err);
        mainWindow.webContents.send("parser-event", {
            type: "log",
            message: `Failed to start parser: ${err.message}`
        });
        mainWindow.webContents.send("parser-event", { type: "error" });
    });

    parser.on("close", (code, signal) => {
        console.log("Parser exited. code =", code, "signal =", signal);

        // If parser ended without sending __DONE__ and it was not a user cancel,
        // treat it as error. If user cancelled, mark it as cancelled.
        if (!hasSignaledDone) {
            if (cancelledByUser) {
                mainWindow.webContents.send("parser-event", {
                    type: "cancelled",
                });
            } else {
                mainWindow.webContents.send("parser-event", {
                    type: "error",
                    exitCode: code,
                });
            }
        }

        currentParser = null;
        cancelledByUser = false;
        hasSignaledDone = false;
    });
});

// Bokeh Dashboard Launcher
ipcMain.on("launch-bokeh", () => {
    try {

        const exePath = getBokehExePath();

        // Example: if you later pass the database path
        const dbPath = getDataPaths().dbPath;

        const bokehProc = spawn(exePath, 
             ["--db", dbPath]
        , {
            detached: true,
            stdio: "ignore"
        });

        bokehProc.unref();

    } catch (err) {

        console.error("Failed to launch Bokeh app:", err);

        if (mainWindow) {
            mainWindow.webContents.send("parser-event", {
                type: "log",
                message: "Failed to launch stats viewer."
            });
        }
    }
});