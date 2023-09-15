import { config } from "dotenv";
import { assertEnv } from "./utils";
config();

export const dbUrl = assertEnv("DB_URL");
export const discordToken = assertEnv('DISCORD_BOT_TOKEN');
export const environment = assertEnv('ENVIRONMENT', "base");
export const logLevel = assertEnv('LOGLEVEL', "info");
