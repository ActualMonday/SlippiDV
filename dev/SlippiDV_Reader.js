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

const { Worker } = require('worker_threads'); // for multi-threading
const fs = require('fs').promises;
const fsSync = require('fs'); // for incremental JSON writing
const path = require('path');
const os = require('os'); // to get number of CPU cores
const cliProgress = require('cli-progress');

// --------------------------------------------------------------
// CONFIGURATION
// --------------------------------------------------------------

const slippiID = "MON#864"; // Your player connect code
const slippiFolderPath = 'C:/Users/Hugh Sharp/Documents/Slippi';
const outputFile = "SlippiDV_FullData.json";

// --------------------------------------------------------------
// Async file listing (recursively)
// --------------------------------------------------------------

async function getAllFileNamesAsync(dirPath) {
    // Returns an array of all file paths (including in subdirectories)
    const entries = await fs.readdir(dirPath, { withFileTypes: true });
    const allFiles = [];

    for (const entry of entries) {
        const fullPath = path.join(dirPath, entry.name);
        if (entry.isDirectory()) {
            // Recursively traverse subdirectory
            const subFiles = await getAllFileNamesAsync(fullPath);
            allFiles.push(...subFiles);
        } else {
            allFiles.push(fullPath);
        }
    }

    return allFiles;
}

// --------------------------------------------------------------
// Load already-processed files (for incremental updates)
// --------------------------------------------------------------

async function loadExistingJSON(filePath) {
    try {
        const data = await fs.readFile(filePath, "utf-8");
        const existingRows = JSON.parse(data);
        const existingFiles = new Set(existingRows.map(r => r.gameFile));
        return { existingRows, existingFiles };
    } catch {
        // If file doesn't exist yet, start fresh
        return { existingRows: [], existingFiles: new Set() };
    }
}

// --------------------------------------------------------------
// Worker Thread Function
// --------------------------------------------------------------

const workerScript = `
const { parentPort, workerData } = require('worker_threads');
const { SlippiGame } = require('@slippi/slippi-js');
const fs = require('fs').promises;

// Worker receives a single file path
const filePath = workerData.filePath;
const slippiID = workerData.slippiID;

// Helper: compute stock damage for a player
function totalStockDmgTaken(playerIndex, stockStats) {
    return stockStats.reduce((sum, s) => sum + (s.playerIndex === playerIndex ? s.endPercent : 0), 0);
}

async function processFile() {
    try {
        const buffer = await fs.readFile(filePath);
        const game = new SlippiGame(buffer);

        const settings = game.getSettings();
        const metadata = game.getMetadata();

        // If missing metadata or not 1v1, send sentinel and exit
        if (!metadata || settings.players.length > 2) {
            parentPort.postMessage(null);
            return;
        }

        // Identify player and opponent, send sentinel and exit if more than 2 players
        let userIndex, oppIndex;
        if (slippiID === settings.players[0].connectCode) {
            userIndex = 0; oppIndex = 1;
        } else if (slippiID === settings.players[1].connectCode) {
            userIndex = 1; oppIndex = 0;
        } else {
            parentPort.postMessage(null);
            return;
        }
        
        // Ignore games <20 sec, send sentinel and exit
        const stats = game.getStats();
        const matchTime = stats.playableFrameCount / 60;
        if (matchTime < 20) {
            parentPort.postMessage(null);
            return;
        }

        const oU = stats.overall[userIndex];
        const oO = stats.overall[oppIndex];
        const aU = stats.actionCounts[userIndex];
        const aO = stats.actionCounts[oppIndex];
        const pU = settings.players[userIndex];
        const pO = settings.players[oppIndex];

        const lCancelU = aU.lCancelCount;
        const lCancelO = aO.lCancelCount;

        const userStockDmgTaken = totalStockDmgTaken(userIndex, stats.stocks);
        const oppStockDmgTaken = totalStockDmgTaken(oppIndex, stats.stocks);

        const matchUserDmg = oU.totalDamage;
        const matchOppDmg = oO.totalDamage;

        let result;
        if (oU.killCount > oO.killCount) result = 1;
        else if (oU.killCount < oO.killCount) result = 0;
        else {
            const userLastStockPercent = matchOppDmg - userStockDmgTaken;
            const oppLastStockPercent = matchUserDmg - oppStockDmgTaken;
            result = userLastStockPercent < oppLastStockPercent ? 1 : 0;
        }

        const userKillStats = { killMoves: [], killPercents: [] };
        const oppKillStats = { killMoves: [], killPercents: [] };

        stats.conversions.forEach(c => {
            if (!c.didKill) return;
            if (c.playerIndex === oppIndex) {
                userKillStats.killMoves.push(c.moves.at(-1)?.moveId);
                userKillStats.killPercents.push(c.endPercent);
            } else if (c.playerIndex === userIndex) {
                oppKillStats.killMoves.push(c.moves.at(-1)?.moveId);
                oppKillStats.killPercents.push(c.endPercent);
            }
        });

        // Send back only the serialized stats (no large objects)
        parentPort.postMessage({
            gameFile: filePath,
            matchResult: result,
            matchStartTime: metadata.startAt,
            stage: settings.stageId,
            gameComplete: stats.gameComplete,
            gameTime: matchTime,
            userConnCode: slippiID,
            userChar: pU.characterId,
            userKills: oU.killCount,
            userDmg: matchUserDmg,
            userIPM: oU.inputsPerMinute.ratio,
            userOCR: oU.successfulConversions.ratio,
            userOPK: oU.openingsPerKill.ratio,
            userNWR: oU.neutralWinRatio.ratio,
            userDPO: oU.damagePerOpening.ratio,
            userDPS: oppStockDmgTaken / oU.killCount,
            userLCR: lCancelU.success / (lCancelU.success + lCancelU.fail),
            userWaveDash: aU.wavedashCount,
            userDashDance: aU.dashDanceCount,
            userGrab: aU.grabCount.success,
            userGrabRatio: aU.grabCount.success / (aU.grabCount.success + aU.grabCount.fail),
            oppConnCode: pO.connectCode,
            oppChar: pO.characterId,
            oppKills: oO.killCount,
            oppDmg: matchOppDmg,
            oppIPM: oO.inputsPerMinute.ratio,
            oppOCR: oO.successfulConversions.ratio,
            oppOPK: oO.openingsPerKill.ratio,
            oppNWR: oO.neutralWinRatio.ratio,
            oppDPO: oO.damagePerOpening.ratio,
            oppDPS: userStockDmgTaken / oO.killCount,
            oppLCR: lCancelO.success / (lCancelO.success + lCancelO.fail),
            oppWaveDash: aO.wavedashCount,
            oppDashDance: aO.dashDanceCount,
            oppGrab: aO.grabCount.success,
            oppGrabRatio: aO.grabCount.success / (aO.grabCount.success + aO.grabCount.fail),
            userKillInfo: userKillStats,
            oppKillInfo: oppKillStats
        });

    } catch (err) {
        // Log error and send a sentinel so main thread keeps going
        console.error('Worker error for', filePath, err && (err.stack || err));
        parentPort.postMessage(null);
    }
}

processFile();
`;

// --------------------------------------------------------------
// Function to run a file in a worker
// --------------------------------------------------------------

// ----------------- improved runWorker with per-worker timeout -----------------
function runWorker(filePath, opts = {}) {
    const workerTimeoutMs = opts.timeoutMs || 60_000; // default 60s per file

    return new Promise((resolve, reject) => {
        const worker = new Worker(workerScript, { eval: true, workerData: { filePath, slippiID } });

        let settled = false;

        // When a message arrives (including null sentinel), resolve with result (or null)
        worker.once('message', result => {
            settled = true;
            resolve(result);
            // allow worker to exit on its own
        });

        worker.once('error', err => {
            if (settled) return;
            settled = true;
            reject(err);
        });

        worker.once('exit', code => {
            if (settled) return;
            // If worker exited without sending a message, resolve with null
            // (we avoid hanging forever)
            settled = true;
            if (code !== 0) {
                reject(new Error(`Worker stopped with exit code ${code}`));
            } else {
                // No message sent but exit successful — treat as null result
                resolve(null);
            }
        });

        // Safety timeout: if a worker takes too long, terminate it and resolve null
        const t = setTimeout(() => {
            if (settled) return;
            settled = true;
            worker.terminate().catch(() => { });
            resolve(null); // treat as rejected/ignored file
        }, workerTimeoutMs);

        // clear the timeout when resolved/rejected
        const cleanup = () => clearTimeout(t);
        // attach cleanup to promise resolution paths
        worker.once('message', cleanup);
        worker.once('error', cleanup);
        worker.once('exit', cleanup);
    });
}
// --------------------------------------------------------------
// Main parser function
// --------------------------------------------------------------

(async () => {
    try {
        // 1. List all files
        const allFiles = await getAllFileNamesAsync(slippiFolderPath);

        // 2. Load existing JSON to skip already-processed games
        const { existingRows, existingFiles } = await loadExistingJSON(outputFile);

        // Filter out already-processed files
        const newFiles = allFiles.filter(f => !existingFiles.has(f));
        console.log(`Found ${newFiles.length} new files to process.`);

        if (newFiles.length === 0) {
            console.log("No new files to process. Exiting.");
            return;
        }

        // 3. Progress bar
        const progressBar = new cliProgress.SingleBar({
            format: 'Processing |{bar}| {percentage}% | {value}/{total} files',
            hideCursor: true
        }, cliProgress.Presets.shades_classic);
        progressBar.start(newFiles.length, 0);

        // 4. Limit concurrency to number of CPU cores
        const cpuCount = os.cpus().length;
        //const concurrency = Math.max(1, cpuCount - 1); // leave 1 core free
        const concurrency = 2;
        let completed = 0;
        const results = [];

        // Process files in batches limited by concurrency
        for (let i = 0; i < newFiles.length; i += concurrency) {
            const batch = newFiles.slice(i, i + concurrency).map(runWorker);
            const batchResults = await Promise.all(batch);
            batchResults.forEach(r => {
                if (r) results.push(r);
            });
            completed += batchResults.length;
            progressBar.update(completed);
        }

        progressBar.stop();

        // 5. Append new results to existing JSON (incremental update)
        const combined = [...existingRows, ...results];
        await fs.writeFile(outputFile, JSON.stringify(combined, null, 2));
        console.log(`Saved ${results.length} new matches. Total matches: ${combined.length}`);

    } catch (err) {
        console.error(err);
    }
})();