const { SlippiGame } = require("@slippi/slippi-js");
const fs = require('fs');
const path = require('path');

//Take slippiID to distinguish player vs opponent
//var slippiID = prompt("Enter your slippi ID (ex: XXX#000): ");
const slippiID = "MON#864";

//Slippi Folder Path
const slippiFolderPath = 'slippifolderlocationhere';

//Function to create array of files including all monthly subdirectories
function getAllFileNames(dirPath, arrayOfFiles) {
    arrayOfFiles = arrayOfFiles || [];

    const files = fs.readdirSync(dirPath);

    files.forEach(function (file) {
        const fullPath = path.join(dirPath, file);
        if (fs.statSync(fullPath).isDirectory()) {
            arrayOfFiles = getAllFileNames(fullPath, arrayOfFiles);
        } else {
            arrayOfFiles.push(fullPath);
        }
    });

    return arrayOfFiles;
}

const fileList = getAllFileNames(slippiFolderPath);

var slippiDict = {
    matchID: [],
    matchResult: [],
    matchStartTime: [],
    stage: [],
    gameComplete: [],
    gameTime: [],
    userConnCode: [],
    userChar: [],
    userKills: [],
    userDmg: [],
    userIPM: [], //inputs per minute
    userOCR: [], //Opening Conversion Rate
    userOPK: [], //Openings Per Kill
    userNWR: [], //Neutral Win Ratio
    userDPO: [], //Damage Per Opening
    userDPS: [], //avg Damage Per Stock
    userLCR: [], //L-Cancel Ratio
    userWaveDash: [],
    userDashDance: [],
    userGrab: [],
    userGrabRatio: [],
    oppConnCode: [],
    oppChar: [],
    oppKills: [],
    oppDmg: [], 
    oppIPM: [], //inputs per minute
    oppOCR: [], //Opening Conversion Rate
    oppOPK: [], //Openings Per Kill
    oppNWR: [], //Neutral Win Ratio
    oppDPO: [], //Damage Per Opening
    oppDPS: [], //avg Damage Per Stock
    oppLCR: [], //L-Cancel Ratio
    oppWaveDash: [],
    oppDashDance: [],
    oppGrab: [],
    oppGrabRatio: []
}

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


for (const gameFile of fileList) {

    const game = new SlippiGame(gameFile);

    // Get game settings – stage, characters, etc
    const settings = game.getSettings();
    // Get metadata - start time, platform played on, etc
    const metadata = game.getMetadata();
    // Get computed stats - openings / kill, conversions, etc
    const stats = game.getStats();

    //check conditions for whether data is ignored///////////////////////////////////////////////////////////
    if (metadata == null) {
        continue;
    }

    if (settings.players.length > 2) {
        continue; //Won't include games that are teams OR > 2 players
    }

    if (slippiID == settings.players[0].connectCode) {
        userIndex = 0;
        oppIndex = 1;
    } else if (slippiID == settings.players[1].connectCode) {
        userIndex = 1;
        oppIndex = 0;
    } else {
        continue; //Won't include gamse that aren't online unfortunately... have to be able to tell who is who
    }

    //check game time. ignore data if <20 sec (arbitrary but feels reasonable for "instant quit outs")
    var matchTime = stats.playableFrameCount / 60;
    if (matchTime < 20) {
        continue;
    }
    /////////////////////////////////////////////////////////////////////////////////////////////////////////
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
    if(oU.killCount > oO.killCount) {
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

    /////////////////////////////////////////////////////////////////////////////////////////////////////////
    //Append Data to Dictionary//////////////////////////////////////////////////////////////////////////////

    //Append Game Info
    slippiDict.matchID.push(settings.matchInfo.matchId);
    slippiDict.matchResult.push(result);
    slippiDict.matchStartTime.push(metadata.startAt);
    slippiDict.stage.push(settings.stageId);
    slippiDict.gameComplete.push(stats.gameComplete);
    slippiDict.gameTime.push(matchTime);

    //Append User Player Info
    slippiDict.userConnCode.push(slippiID);
    slippiDict.userChar.push(pU.characterId);
    slippiDict.userKills.push(oU.killCount);
    slippiDict.userDmg.push(matchUserDmg);
    slippiDict.userIPM.push(oU.inputsPerMinute.ratio);
    slippiDict.userOCR.push(oU.successfulConversions.ratio);
    slippiDict.userOPK.push(oU.openingsPerKill.ratio);
    slippiDict.userNWR.push(oU.neutralWinRatio.ratio);
    slippiDict.userDPO.push(oU.damagePerOpening.ratio);
    slippiDict.userDPS.push(totalStockDmgTaken(oppIndex, stats.stocks) / oU.killCount);
    slippiDict.userLCR.push(lCancelU.success / (lCancelU.success + lCancelU.fail));
    slippiDict.userWaveDash.push(aU.wavedashCount);
    slippiDict.userDashDance.push(aU.dashDanceCount);
    slippiDict.userGrab.push(aU.grabCount.success);
    slippiDict.userGrabRatio.push(aU.grabCount.success / (aU.grabCount.success + aU.grabCount.fail));

    //Append Opponent Player Info
    slippiDict.oppConnCode.push(pO.connectCode);
    slippiDict.oppChar.push(pO.characterId);
    slippiDict.oppKills.push(oO.killCount);
    slippiDict.oppDmg.push(matchOppDmg);
    slippiDict.oppIPM.push(oO.inputsPerMinute.ratio);
    slippiDict.oppOCR.push(oO.successfulConversions.ratio);
    slippiDict.oppOPK.push(oO.openingsPerKill.ratio);
    slippiDict.oppNWR.push(oO.neutralWinRatio.ratio);
    slippiDict.oppDPO.push(oO.damagePerOpening.ratio);
    slippiDict.oppDPS.push(totalStockDmgTaken(userIndex, stats.stocks) / oO.killCount);
    slippiDict.oppLCR.push(aO.lCancelCount.success / (aO.lCancelCount.success + aO.lCancelCount.fail));
    slippiDict.oppWaveDash.push(aO.wavedashCount);
    slippiDict.oppDashDance.push(aO.dashDanceCount);
    slippiDict.oppGrab.push(aO.grabCount.success);
    slippiDict.oppGrabRatio.push(aO.grabCount.success / (aO.grabCount.success + aO.grabCount.fail));

    console.log(gameFile) //printing matchID showed duplicates, but printing gameFile doesn't... no clue why
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////
//Write Dat File

const jsonString = JSON.stringify(slippiDict, null, 2);
    
fs.writeFileSync("SlippiDV_FullData.dat", jsonString)