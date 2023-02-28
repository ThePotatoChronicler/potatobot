import xkcd from './xkcd';
import version from './version';
import start_elevator_trial from './start_elevator_trial';
import type { SlashCommand } from '../types';

export const slashCommands: SlashCommand[] = [
	xkcd,
	version,
	start_elevator_trial
]

export const slashCommandsHandlerMap = new Map(slashCommands.map(c => {
	return [c.name, c.handler]
}))

export {
	version,
	xkcd,
}
