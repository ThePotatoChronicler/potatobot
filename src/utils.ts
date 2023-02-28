import { logger } from "./logger";

export function assertEnv(key: string, backup?: string): string | never {
	const val = process.env[key];
	if (val !== undefined) {
		return val;
	}

	if (backup !== undefined) {
		return backup;
	}

	logger.error(`Missing required environment value '${key}'`);

	// Returned to satisfy the "never" type return
	return process.exit(1);
}
