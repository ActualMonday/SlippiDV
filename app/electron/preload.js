const { contextBridge, ipcRenderer } = require("electron");


contextBridge.exposeInMainWorld("api", {
    
    selectFolder: () => ipcRenderer.invoke("select-folder"),

    onParserLog: (callback) => {
        ipcRenderer.on("parser-log", (_, message) => {
            callback(message);
        });
    },

    runParser: (slippiFolderPath, slippiID) =>
        ipcRenderer.send("run-parser", { slippiFolderPath, slippiID }),

    cancelParser: () =>
        ipcRenderer.send("cancel-parser"),

    launchBokeh: () => ipcRenderer.send("launch-bokeh"),

    onParserEvent: (callback) =>
        ipcRenderer.on("parser-event", (_, data) => callback(data))


});


