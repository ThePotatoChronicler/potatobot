import pino from "pino";

const pretty = process.env["LOGPRETTY"] !== undefined;

const options: pino.LoggerOptions = {
	name: "potatobot",
	level: process.env["LOGLEVEL"] ?? "warn",
};

if (pretty) {
	options.transport = {
		target: 'pino-pretty'
	};
}

export const logger = pino(options);
