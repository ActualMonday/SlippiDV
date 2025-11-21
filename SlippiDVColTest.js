const { SlippiGame } = require("@slippi/slippi-js");
const fs = require("fs").promises;
const fsSync = require("fs"); // for typical file system uses
const path = require('path');
const pLimit = require("p-limit");
const cliProgress = require("cli-progress");

//Take slippiID to distinguish player vs opponent
//var slippiID = prompt("Enter your slippi ID (ex: XXX#000): ");
const slippiID = "MON#864";

//Slippi Folder Path
const slippiFolderPath = 'C:/Users/Hugh Sharp/Documents/Slippi';

//Function to create array of files including all monthly subdirectories
function getAllFileNames(dirPath, arrayOfFiles) {
    arrayOfFiles = arrayOfFiles || [];

    const files = fsSync.readdirSync(dirPath);

    files.forEach(function (file) {
        const fullPath = path.join(dirPath, file);
        if (fsSync.statSync(fullPath).isDirectory()) {
            arrayOfFiles = getAllFileNames(fullPath, arrayOfFiles);
        } else {
            arrayOfFiles.push(fullPath);
        }
    });

    return arrayOfFiles;
}

const fileList = getAllFileNames(slippiFolderPath);


//Create function to determine damage done during stock kills
//needed to find avg dmg per stock, and determine who wins in a timeout
function totalStockDmgTaken(playerIndex, stockStats) {
    var totalDmg = 0;
    for (const stock of stockStats) {
        if (stock.playerIndex == playerIndex) {
            totalDmg += stock.endPercent;
        }
        else {
            continue;
        }
    }
    return totalDmg;
}

//asyncronously read slippi files concurrently to maximize speed going through those HUGE slippi folders
//looking at cody and zain lmao

// need to import p-limit dynamically so I'll do so below calling "loadSlippiFiles"

async function loadSlippiFiles(fileList, limitUsed) {

    //Create Progress Bar

    //Create Progress Bar
    const progressBar = new cliProgress.SingleBar({
        format: 'Processing |{bar}| {percentage}% | {value}/{total} files | ETA: {eta_formatted}',
        hideCursor: true,
    }, cliProgress.Presets.shades_classic);

    let completed = 0;
    progressBar.start(fileList.length, 0);

    //attach progress to rowPromises
    // Create one promise per file, processed with concurrency limit
    const rowPromises = fileList.map(filePath =>
        limitUsed(async () => {
            const row = await processSlpFile(filePath);
            completed++;
            progressBar.update(completed);
            return row;
        })
    );

    // Create one promise per file, processed with concurrency limit
    //const rowPromises = fileList.map(filePath =>
        //limitUsed(() => processSlpFile(filePath)) //calling individual slp file processing function written below
    //);

    // Wait for all processing to finish
    const rows = await Promise.all(rowPromises);

    // Remove null entries (errors, invalid files, <20 sec matches)
    return rows.filter(Boolean);
}

//Individual Slippi File Processing
async function processSlpFile(filePath) {
    try {
        const buffer = await fs.readFile(filePath);
        const game = new SlippiGame(buffer);

        //get game settings, metadata, and stats
        const settings = game.getSettings();
        const metadata = game.getMetadata();
        const stats = game.getStats();

        //check conditions for whether data is ignored///////////////////////////////////////////////////////////
        if (metadata == null) {
            return null;
        }
        if (settings.players.length > 2) {
            return null; //Won't include games that are teams OR > 2 players
        }

        if (slippiID == settings.players[0].connectCode) {
            userIndex = 0;
            oppIndex = 1;
        } else if (slippiID == settings.players[1].connectCode) {
            userIndex = 1;
            oppIndex = 0;
        } else {
            return null; //Won't include games that aren't online unfortunately... have to be able to tell who is who
        }
        //check game time. ignore data if <20 sec (arbitrary but feels reasonable for "instant quit outs")
        var matchTime = stats.playableFrameCount / 60;
        if (matchTime < 20) {
            return null;
        }
        ///////////////////////////////////////////////////////////////////////////////////////////////////////////
        //Calulate necesarry things to add data in///////////////////////////////////////////////////////////////

        //cache common references
        const oU = stats.overall[userIndex];
        const oO = stats.overall[oppIndex];
        const aU = stats.actionCounts[userIndex];
        const aO = stats.actionCounts[oppIndex];
        const pU = settings.players[userIndex];
        const pO = settings.players[oppIndex];

        const lCancelU = aU.lCancelCount;
        const lCancelO = aO.lCancelCount;

        //find dmg totals to determine win if timeout
        var matchUserDmg = oU.totalDamage;
        var matchOppDmg = oO.totalDamage;

        //determine who won
        if (oU.killCount > oO.killCount) {
            result = 1; //win
        } else if (oU.killCount < oO.killCount) {
            result = 0; //loss
        } else {//if goes to time
            userLastStockPercent = matchOppDmg - totalStockDmgTaken(userIndex, stats.stocks);
            oppLastStockPercent = matchUserDmg - totalStockDmgTaken(oppIndex, stats.stocks);
            if (userLastStockPercent < oppLastStockPercent) {
                result = 1;
            } else {
                result = 0;
            }
        }
        return {

            //Match-Level Info
            matchID: settings.matchInfo.matchId,
            matchResult: result,
            matchStartTime: metadata.startAt,
            stage: settings.stageId,
            gameComplete: stats.gameComplete,
            gameTime: matchTime,

            //User-Level Info
            userConnCode: slippiID,
            userChar: pU.characterId,
            userKills: oU.killCount,
            userDmg: matchUserDmg,
            userIPM: oU.inputsPerMinute.ratio,
            userOCR: oU.successfulConversions.ratio,
            userOPK: oU.openingsPerKill.ratio,
            userNWR: oU.neutralWinRatio.ratio,
            userDPO: oU.damagePerOpening.ratio,
            userDPS: totalStockDmgTaken(oppIndex, stats.stocks) / oU.killCount,
            userLCR: lCancelU.success / (lCancelU.success + lCancelU.fail),
            userWaveDash: aU.wavedashCount,
            userDashDance: aU.dashDanceCount,
            userGrab: aU.grabCount.success,
            userGrabRatio: aU.grabCount.success / (aU.grabCount.success + aU.grabCount.fail),

            //Opponent-Level Info
            oppConnCode: pO.connectCode,
            oppChar: pO.characterId,
            oppKills: oO.killCount,
            oppDmg: matchOppDmg,
            oppIPM: oO.inputsPerMinute.ratio,
            oppOCR: oO.successfulConversions.ratio,
            oppOPK: oO.openingsPerKill.ratio,
            oppNWR: oO.neutralWinRatio.ratio,
            oppDPO: oO.damagePerOpening.ratio,
            oppDPS: totalStockDmgTaken(userIndex, stats.stocks) / oO.killCount,
            oppLCR: lCancelO.success / (lCancelO.success + lCancelO.fail),
            oppWaveDash: aO.wavedashCount,
            oppDashDance: aO.dashDanceCount,
            oppGrab: aO.grabCount.success,
            oppGrabRatio: aO.grabCount.success / (aO.grabCount.success + aO.grabCount.fail),
        };
        /////////////////////////////////////////////////////////////////////////////////////////////////////////
    } catch (err) {
        console.error(`Error processing ${filePath}:`, err)
        return null;
    }
}


/////////////////////////////////////////////////////////////////////////////////////////////////////////
//Write Dat File and Apply Concurrency limiter
(async () => {
    const pLimit = await import('p-limit').then(mod => mod.default);
    const limit = pLimit(16); //limits concurrent file read to 16 to avoid memory issues

    const rows = await loadSlippiFiles(fileList, limit);
    console.log(`Processed ${rows.length} matches`); //report number of matches

    fsSync.writeFileSync("SlippiDV_FullData.json", JSON.stringify(rows, null, 2));
})();