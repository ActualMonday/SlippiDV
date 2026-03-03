const { SlippiGame } = require("@slippi/slippi-js");
const fs = require('fs');

//Take slippiID to distinguish player vs opponent
//var slippiID = prompt("Enter your slippi ID (ex: XXX#000): ");
const slippiID = "MON#864"

//Slippi Folder Path
//const slippiFolderPath = 

//set up arrays to for later dat file
//user arrays
const userCharID = [];
const userAvgDP = [];
//opp arrays
const oppCharID = [];
const oppAvgDP = [];
//neutral arrays
const StageID = [];

const game = new SlippiGame("test.slp");

// Get game settings – stage, characters, etc
const settings = game.getSettings();
console.log(settings);

// Get metadata - start time, platform played on, etc
const metadata = game.getMetadata();
console.log(metadata);

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



console.log(settings.players[userIndex].characterId);
console.log(stats.overall[userIndex].openingsPerKill);



console.log(settings.matchInfo.matchId);

console.log(settings.players.length);

console.log(frames[-1].players);

console.log(metadata);


// const data = [1, null, "hello", 0, undefined, { key: null }];
// const filteredData = data.filter(Boolean);
// console.log(filteredData);
// Output: [1, "hello", { key: "value" }]

// console.log(stats.combos[].attackCount);

const killStats = {
	killMoves: [],
	killPercents: []
};

stats.conversions
	.filter(c => c.didKill && c.playerIndex === userIndex)
	.forEach(c => {
		killStats.killMoves.push(c.moves.at(-1)?.moveId);
		killStats.killPercents.push(c.endPercent);
	});
console.log(killStats)