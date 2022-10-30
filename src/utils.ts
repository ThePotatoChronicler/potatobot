import { logger } from "./logger";

export function assertEnv(key: string, backup?: string): string | never {
	const val = process.env[key];
	if (val === undefined) {
		if (backup !== undefined) {
			return backup;
		}
		logger.error(`Missing required environment value '${key}'`);
		return process.exit(1);
	}
	return val;
}
