import pino from "pino";

export const logger = pino({
	level: process.env["LOGLEVEL"] ?? "info",
	transport: {
		target: 'pino-pretty'
	},
});
