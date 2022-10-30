import xkcd from './xkcd';
import version from './version';

export const slashCommandsMap = new Map(Object.entries({
	xkcd,
	version,
}));

export {
	version,
	xkcd,
}
