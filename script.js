const { SlippiGame } = require("@slippi/slippi-js");

//Take slippiID to distinguish player vs opponent
//var slippiID = prompt("Enter your slippi ID (ex: XXX#000): ");
const slippiID = "MON#864"

//set up arrays to for later dat file
const userCharID = [];
const oppCharID = [];
const StageID = [];
const userAvgDP = [];
const oppAvgDP = [];


const game = new SlippiGame("Game_20250116T162103.slp");

// Get game settings – stage, characters, etc
const settings = game.getSettings();
console.log(settings);

// Get metadata - start time, platform played on, etc
const metadata = game.getMetadata();
//console.log(metadata);

// Get computed stats - openings / kill, conversions, etc
const stats = game.getStats();
console.log(stats);

// Get frames – animation state, inputs, etc
// This is used to compute your own stats or get more frame-specific info (advanced)
const frames = game.getFrames();
//console.log(frames[0].players); // Print frame when timer starts counting down

if (slippiID == settings.players[0].connectCode) {
	userIndex = 0
	oppIndex = 1
} else {
	userIndex = 1
	oppIndex = 0
	console.log(slippiID == settings.players[1].connectCode)
}


const playercharid = settings.players[1].characterID;
console.log(playercharid);
console.log(settings.players[0].characterId);
console.log(stats.overall[userIndex].openingsPerKill)