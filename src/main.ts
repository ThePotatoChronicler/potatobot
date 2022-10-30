import { Client } from "discord.js";
import { dbUrl, discordToken, environment } from "./env";
import { registerGlobalCommands } from "./appcommands";
import { logger } from "./logger";
import { MongoClient } from "mongodb";
import { replitStart } from "./replit_keepalive";
import { xkcd, version as versionCmd } from "./commands";

if (environment === 'replit') {
	logger.info("Starting replit keep_alive");
	replitStart();
}

logger.info("Connecting to DB");
const dbclient = new MongoClient(dbUrl);
await dbclient.connect();
logger.info("Connected to DB");

await registerGlobalCommands(dbclient);

const client = new Client({
	intents: 0
});

client.once('ready', client => {
	logger.info({username: client.user.tag}, `Ready and serving ${client.guilds.cache.size} guild(s)`);
});

client.on('interactionCreate', async interaction => {
	if (interaction.isChatInputCommand()) {
		if (interaction.commandName === "xkcd") {
			await xkcd(interaction);
		}

		if (interaction.commandName === "version") {
			await versionCmd(interaction);
		}
	}
});

client.on('warn', (message) => {
	logger.warn({ from: "discord.js" }, message);
});

client.on('debug', (message) => {
	logger.debug({ from: "discord.js" }, message);
});

await client.login(discordToken);
