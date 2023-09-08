import { assertEnv } from "./utils";

export const dbUrl = assertEnv("DB_URL");
export const discordToken = assertEnv('DISCORD_BOT_TOKEN');
export const applicationID = assertEnv('DISCORD_APPLICATION_ID');
export const environment = assertEnv('ENVIRONMENT', "base");
export const logLevel = assertEnv('LOGLEVEL', "info");
