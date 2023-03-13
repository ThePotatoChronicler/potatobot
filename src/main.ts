import { Client, GatewayIntentBits } from "discord.js";
import { dbUrl, discordToken, environment } from "./env";
import { registerGlobalCommands } from "./appcommands";
import { logger } from "./logger";
import { MongoClient } from "mongodb";
import { replitStart } from "./replit_keepalive";
import { slashCommandsHandlerMap } from "./commands";
import { constructHandler as constructElevatorHandler } from "./elevator_handler";
import { handler as messageComponentHandler } from "./message_component_handler";

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
	intents: GatewayIntentBits.Guilds | GatewayIntentBits.GuildVoiceStates
});

const elevatorHandler = constructElevatorHandler(client, dbclient);

let exitCalled = false;
const exitListener = () => {
	if (exitCalled) {
		return;
	}
	exitCalled = true;
	const _exitPromise = (async () => {
		elevatorHandler[0].abort("The process is exiting");
		await elevatorHandler[1].catch(e => {
			if (e instanceof Error && e.name === "AbortError") {
				return;
			}
			logger.error({ error: e as unknown }, "Error occurred in elevator handler");
		});

		client.destroy();
		process.exit(0);
	})();
};

process.on("SIGINT", exitListener)
process.on("SIGTERM", exitListener)

client.once('ready', client => {
	logger.info({username: client.user.tag}, `Ready and serving ${client.guilds.cache.size} guild(s)`);
});

client.on('interactionCreate', async interaction => {
	if (interaction.isChatInputCommand()) {
		const handler = slashCommandsHandlerMap.get(interaction.commandName);
		try {
			await handler?.({
				interaction,
				mongodb: dbclient
			});
		} catch (e) {
			logger.error({ exception: e }, "Uncaught exception in slash command handler, continuing regardless");
		}
	}

	if (interaction.isMessageComponent()) {
		await messageComponentHandler({ interaction, mongodb: dbclient });
	}
});

client.on('warn', (message) => {
	logger.warn({ from: "discord.js" }, message);
});

client.on('debug', (message) => {
	logger.debug({ from: "discord.js" }, message);
});

await client.login(discordToken);
