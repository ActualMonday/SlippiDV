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
const cliProgress = require('cli-progress');
const { createWorkerPool } = require('./workerPool');

const [, , slippiFolderPath, slippiID] = process.argv;

if (!slippiFolderPath || !slippiID) {
    console.error("Missing slippi folder path and/or player connection code");
    process.exit(1);
}

console.log("Parsing slippi files from:", slippiFolderPath);
console.log("Connection Code:", slippiID);


const outputFile = 'SlippiDV_FullData.json';
const rejectedFile = 'rejected_files.txt';


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
    const allFiles = await getAllFileNames(slippiFolderPath);
    const { existingRows, existingFiles } = await loadExistingJSON(outputFile);

    let rejectedSet = new Set();
    try {
        const rejectedData = await fs.readFile(rejectedFile, 'utf-8');
        rejectedSet = new Set(rejectedData.split('\n').filter(Boolean));
    } catch { }

    const newFiles = allFiles.filter(f => !existingFiles.has(f) && !rejectedSet.has(f));
    console.log(`Found ${newFiles.length} new files.`);

    if (!newFiles.length) return console.log('No new files to process.');

    //const progressBar = new cliProgress.SingleBar({
    //    format: 'Processing |{bar}| {percentage}% | {value}/{total} files',
    //    hideCursor: true
    //}, cliProgress.Presets.shades_classic);

    //progressBar.start(newFiles.length, 0);

    const results = [];
    const rejectedFiles = [];

    const pool = createWorkerPool(slippiID);

    for (const filePath of newFiles) {
        const msg = await pool.runTask(filePath);

        if (msg.rejected) rejectedFiles.push(msg.filePath);
        else results.push(msg.data);

        const progressPercent =
            ((results.length + rejectedFiles.length) / newFiles.length) * 100;

        process.stdout.write(JSON.stringify({
            type: "progress",
            value: progressPercent
        }) + "\n");

        process.stdout.write(JSON.stringify({
            type: "log",
            message: `Processed ${filePath}`
        }) + "\n");
    }

    //progressBar.stop();

    const combined = [...existingRows, ...results];
    await fs.writeFile(outputFile, JSON.stringify(combined, null, 2));
    console.log(`Saved ${results.length} new matches. Total matches: ${combined.length}`);

    if (rejectedFiles.length) {
        await fs.writeFile(rejectedFile, rejectedFiles.join('\n') + '\n', { flag: 'a' });
        console.log(`Saved ${rejectedFiles.length} rejected files.`);
    }

    await pool.terminateAll();
})();