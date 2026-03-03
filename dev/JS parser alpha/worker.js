/**
 * Worker thread script — processes a single Slippi file
 */

const { parentPort, workerData } = require('worker_threads');
const { SlippiGame } = require('@slippi/slippi-js');
const fs = require('fs').promises;

// Receive shared utility functions via workerData
const { slippiID } = workerData;

// Compute total stock damage taken
function totalStockDmgTaken(playerIndex, stockStats) {
    return stockStats.reduce((sum, s) => sum + (s.playerIndex === playerIndex ? s.endPercent : 0), 0);
}

// Listen for file path messages
parentPort.on('message', async (filePath) => {
    try {
        const buffer = await fs.readFile(filePath);
        const game = new SlippiGame(buffer);

        const settings = game.getSettings();
        const metadata = game.getMetadata();

        if (!metadata || settings.players.length > 2) {
            parentPort.postMessage({ rejected: true, filePath });
            return;
        }

        let userIndex, oppIndex;
        if (slippiID === settings.players[0].connectCode) {
            userIndex = 0; oppIndex = 1;
        } else if (slippiID === settings.players[1].connectCode) {
            userIndex = 1; oppIndex = 0;
        } else if (slippiID === "player 1") {
            userIndex = 0; oppIndex = 1;
        } else {
            parentPort.postMessage({ rejected: true, filePath });
            return;
        }

        const stats = game.getStats();
        const matchTime = stats.playableFrameCount / 60;
        if (matchTime < 20) {
            parentPort.postMessage({ rejected: true, filePath });
            return;
        }

        const oU = stats.overall[userIndex];
        const oO = stats.overall[oppIndex];
        const aU = stats.actionCounts[userIndex];
        const aO = stats.actionCounts[oppIndex];
        const pU = settings.players[userIndex];
        const pO = settings.players[oppIndex];

        let result;
        if (oU.killCount > oO.killCount) result = 1;
        else if (oU.killCount < oO.killCount) result = 0;
        else {
            const userLastStockPercent = oO.totalDamage - totalStockDmgTaken(userIndex, stats.stocks);
            const oppLastStockPercent = oU.totalDamage - totalStockDmgTaken(oppIndex, stats.stocks);
            result = userLastStockPercent < oppLastStockPercent ? 1 : 0;
        }

        // Build kill stats
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

        parentPort.postMessage({
            rejected: false,
            data: {
                gameFile: filePath,
                matchResult: result,
                matchStartTime: metadata.startAt,
                stage: settings.stageId,
                gameComplete: stats.gameComplete,
                gameTime: matchTime,
                userConnCode: slippiID,
                userChar: pU.characterId,
                userKills: oU.killCount,
                userDmg: oU.totalDamage,
                userIPM: oU.inputsPerMinute.ratio,
                userOCR: oU.successfulConversions.ratio,
                userOPK: oU.openingsPerKill.ratio,
                userNWR: oU.neutralWinRatio.ratio,
                userDPO: oU.damagePerOpening.ratio,
                userDPS: totalStockDmgTaken(oppIndex, stats.stocks) / oU.killCount,
                userLCR: aU.lCancelCount.success / (aU.lCancelCount.success + aU.lCancelCount.fail),
                userWaveDash: aU.wavedashCount,
                userDashDance: aU.dashDanceCount,
                userGrab: aU.grabCount.success,
                userGrabRatio: aU.grabCount.success / (aU.grabCount.success + aU.grabCount.fail),
                oppConnCode: pO.connectCode,
                oppChar: pO.characterId,
                oppKills: oO.killCount,
                oppDmg: oO.totalDamage,
                oppIPM: oO.inputsPerMinute.ratio,
                oppOCR: oO.successfulConversions.ratio,
                oppOPK: oO.openingsPerKill.ratio,
                oppNWR: oO.neutralWinRatio.ratio,
                oppDPO: oO.damagePerOpening.ratio,
                oppDPS: totalStockDmgTaken(userIndex, stats.stocks) / oO.killCount,
                oppLCR: aO.lCancelCount.success / (aO.lCancelCount.success + aO.lCancelCount.fail),
                oppWaveDash: aO.wavedashCount,
                oppDashDance: aO.dashDanceCount,
                oppGrab: aO.grabCount.success,
                oppGrabRatio: aO.grabCount.success / (aO.grabCount.success + aO.grabCount.fail),
                userKillInfo: userKillStats,
                oppKillInfo: oppKillStats
            }
        });

    } catch (err) {
        console.error('Worker error:', filePath, err);
        parentPort.postMessage({ rejected: true, filePath });
    }
});