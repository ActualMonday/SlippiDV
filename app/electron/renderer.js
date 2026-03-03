window.addEventListener("DOMContentLoaded", () => {
    const folderInput = document.getElementById("folderInput");
    const browseButton = document.getElementById("browseButton");
    const runButton = document.getElementById("runButton");
    const cancelButton = document.getElementById("cancelButton");
    const output = document.getElementById("output");
    const progressBar = document.getElementById("progressBar");
    const progressLabel = document.getElementById("progressLabel");
    const launchBokehButton = document.getElementById("launchBokehButton");
    const lastParseDate = document.getElementById("lastParseDate");
    const idInput = document.getElementById("idInput");   // ELEMENT, not .value

    // Browse button
    browseButton.addEventListener("click", async () => {
        const folderPath = await window.api.selectFolder();
        if (folderPath) folderInput.value = folderPath;
    });

    // Run parser button
    runButton.addEventListener("click", () => {
        const folder = folderInput.value;
        const slippiID = idInput.value;

        if (!folder) {
            output.textContent += "Please select a Slippi folder first.\n";
            return;
        }

        output.textContent = "";
        if (progressBar) progressBar.value = 0;
        if (progressLabel) progressLabel.textContent = "";

        runButton.disabled = true;
        cancelButton.disabled = false;

        window.api.runParser(folder, slippiID);
    });

    // Cancel parser
    cancelButton.addEventListener("click", () => {
        window.api.cancelParser();
        cancelButton.disabled = true; // prevent spamming
    });

    // Bokeh Button
    launchBokehButton.addEventListener("click", () => {
        window.api.launchBokeh();
    });

    // Handle events from parser
    window.api.onParserEvent((event) => {
        console.log("EVENT RECEIVED:", event); // debug

        if (event.type === "last-parse") {
            const d = new Date(event.value);
            lastParseDate.textContent = `${d.toLocaleString()}`;
        }

        if (event.type === "done") {
            runButton.disabled = false;
            cancelButton.disabled = true;
            const now = new Date();
            lastParseDate.textContent = `${now.toLocaleString()}`;
        }

        if (event.type === "progress") {
            if (progressBar && typeof event.value === "number") {
                progressBar.value = event.value;
            }

            if (progressLabel && typeof event.done === "number" && typeof event.total === "number") {
                const pct = event.value.toFixed(1); // 1 decimal place
                progressLabel.textContent = `${pct}% (${event.done}/${event.total} files)`;
            }
        }

        if (event.type === "log") {
            if (output) {
                output.textContent += event.message + "\n";
                output.scrollTop = output.scrollHeight;
            }
        }

        if (event.type === "done" || event.type === "cancelled") {
            runButton.disabled = false;
            cancelButton.disabled = true;
        }

        if (event.type === "cancelled") {
            runButton.disabled = false;
            cancelButton.disabled = true;
        }

        if (event.type === "error") {
            runButton.disabled = false;
            cancelButton.disabled = true;
        }
    });
});