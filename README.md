SlippiDV

SlippiDV is a local analytics tool for Super Smash Bros. Melee Slippi replays.

It parses .slp replay files and generates an interactive dashboard showing gameplay statistics such as:

win rate

damage per stock

neutral win rate

kill percent distributions

opponent statistics

time-based performance trends

The application consists of three components:

Component	Purpose
Parser (Node.js)	Reads .slp files and builds a structured match database
Electron App	Provides a simple desktop interface to run the parser and launch the dashboard
Bokeh Dashboard (Python)	Displays interactive statistics and charts
