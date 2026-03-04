/**
 * ================================================================
 * High-Performance Slippi Parser with Worker Threads
 * ================================================================
 *
 * This parser is optimized for very large Slippi collections.
 * It uses multiple worker threads to parse CPU-heavy .slp files
 * in parallel, pre-filters unwanted games, and writes results
 * incrementally to a JSON file to avoid memory issues.
 *
 */

// main.js
/**
 * Main entry point — orchestrates file discovery, persistent worker pool, JSON writing
 */

const fs = require('fs').promises;
const fsSync = require('fs');
const path = require('path');
const { createWorkerPool } = require('./workerPool');

const [, , slippiFolderPath, slippiID] = process.argv;

if (!slippiFolderPath || !slippiID) {
    console.error("Missing slippi folder path and/or player connection code");
    process.exit(1);
}

//console.log("Parsing slippi files from:", slippiFolderPath);
//console.log("Connection Code:", slippiID);


const outputFile = '../user_data/SlippiDV_FullData.json';
const rejectedFile = '../user_data/rejected_files.txt';

function emitProgress(done, total) {
    const value = total > 0 ? (done / total) * 100 : 100;

    // Prefix progress lines so Electron can detect them
    process.stdout.write(
        "__PROGRESS__" +
        JSON.stringify({
            value,
            done,
            total,
        }) +
        "\n"
    );
}

// ----------------- Helper functions -----------------
async function getAllFileNames(dirPath) {
    const entries = await fs.readdir(dirPath, { withFileTypes: true });
    const allFiles = [];
    for (const entry of entries) {
        const fullPath = path.join(dirPath, entry.name);
        if (entry.isDirectory()) {
            const subFiles = await getAllFileNames(fullPath);
            allFiles.push(...subFiles);
        } else {
            allFiles.push(fullPath);
        }
    }
    return allFiles;
}

async function loadExistingJSON(filePath) {
    try {
        const data = await fs.readFile(filePath, 'utf-8');
        const existingRows = JSON.parse(data);
        const existingFiles = new Set(existingRows.map(r => r.gameFile));
        return { existingRows, existingFiles };
    } catch {
        return { existingRows: [], existingFiles: new Set() };
    }
}

// ----------------- Main -----------------
(async () => {
    const [, , slippiFolderPath, slippiID] = process.argv;

    console.log(`Parsing slippi files from: ${slippiFolderPath}`);
    console.log(`Connection Code: ${slippiID}`);

    // This can be a plain log now; doesn't need JSON
    

    const allFiles = await getAllFileNames(slippiFolderPath);
    const { existingRows, existingFiles } = await loadExistingJSON(outputFile);

    let rejectedSet = new Set();
    try {
        const rejectedData = await fs.readFile(rejectedFile, "utf-8");
        rejectedSet = new Set(rejectedData.split("\n").filter(Boolean));
    } catch { }

    const newFiles = allFiles.filter(
        (f) => !existingFiles.has(f) && !rejectedSet.has(f)
    );

    console.log(`Found ${newFiles.length} new files.`);

    if (!newFiles.length) {
        emitProgress(1, 1); // 100% immediately
        return;
    }

    const results = [];
    const rejectedFiles = []; 

    let doublesCount = 0;
    let invalididCount = 0;
    let quitoutCount = 0;

    const pool = createWorkerPool(slippiID);

    let done = 0;
    const total = newFiles.length;

    for (const filePath of newFiles) {
        const msg = await pool.runTask(filePath);

        //used to just be msg.rejected and 1 if statement
        if (msg.rejected) {
            rejectedFiles.push(msg.filePath);

            if (msg.rejected === "doubles") {
                doublesCount++;
            } else if (msg.rejected === "invalidid") {
                invalididCount++;
            } else if (msg.rejected === "quitout") {
                quitoutCount++;
            }
        } else {
            results.push(msg.data);
        }

        done += 1;
        emitProgress(done, total);  // drives the Electron progress bar

        // Optional: keep or remove
        //console.log(`Processed ${done}/${total} files`);
    }

    const combined = [...existingRows, ...results];
    await fs.writeFile(outputFile, JSON.stringify(combined, null, 2));
    console.log(`Saved ${results.length} new matches. Total matches: ${combined.length}`);

    if (rejectedFiles.length) {
        await fs.writeFile(rejectedFile, rejectedFiles.join('\n') + '\n', { flag: 'a' });
        console.log(`Saved ${rejectedFiles.length} rejected files to be skipped in future pareses:`);
        console.log(` - ${doublesCount} doubles matches`);
        console.log(` - ${invalididCount} matches offline/no matching slippi player connection code`);
        console.log(` - ${quitoutCount} games quit in <20 sec`);
    }

    await pool.terminateAll();
    process.stdout.write("__DONE__\n");
})();