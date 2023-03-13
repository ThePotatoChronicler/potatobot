import xkcd from './xkcd';
import version from './version';
import start_elevator_trial from './start_elevator_trial';
import settings_ui from './settings_ui';
import push_emoji from './push_emoji';
import type { SlashCommand } from '../types';

export const slashCommands: SlashCommand[] = [
	xkcd,
	version,
	start_elevator_trial,
	settings_ui,
	push_emoji,
]

export const slashCommandsHandlerMap = new Map(slashCommands.map(c => {
	return [c.name, c.handler]
}))

export {
	version,
	xkcd,
}
