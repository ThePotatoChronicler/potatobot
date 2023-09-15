import xkcd from './xkcd';
import version from './version';
import elevator_trial from './elevator_trial';
import settings_ui from './settings_ui';
import push_emoji from './push_emoji';
import renameall from './renameall';
import type { SlashCommand } from '../types';

export const slashCommands: SlashCommand[] = [
	xkcd,
	version,
	elevator_trial,
	settings_ui,
	push_emoji,
	renameall,
]

export const slashCommandsHandlerMap = new Map(slashCommands.map(c => {
	return [c.name, c.handler]
}))

export {
	version,
	xkcd,
}
