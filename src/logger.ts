import winston from "winston";

const pretty = process.env["LOGPRETTY"] !== undefined;

const options: winston.LoggerOptions = {
	level: process.env["LOGLEVEL"] ?? "warn",
	transports: [],
	exitOnError: false,
};

export const logger = winston.createLogger(options);

if (pretty) {
	logger.add(new winston.transports.Console({
		format: winston.format.combine(
			winston.format.timestamp(),
			winston.format.prettyPrint({
				colorize: true,
			}),
		)
	}));
}
