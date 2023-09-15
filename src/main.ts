import { Client, GatewayIntentBits } from "discord.js";
import { dbUrl, discordToken, environment } from "./env";
import { registerGlobalCommands } from "./appcommands";
import { logger } from "./logger";
import { MongoClient } from "mongodb";
import { replitStart } from "./replit_keepalive";
import { slashCommandsHandlerMap } from "./commands";
import { handler as elevatorHandler } from "./elevator_handler";
import { handler as messageComponentHandler } from "./message_component_handler";
import { initializeLists, setupRestartedRenameall } from "./renameall";
import _ from "lodash-es";
// import { setupSettingsChangeHandler } from "./settings_change_handler";

if (environment === 'replit') {
	logger.info("Starting replit keep_alive");
	replitStart();
}

logger.info("Connecting to DB");
const dbclient = new MongoClient(dbUrl);
await dbclient.connect();
logger.info("Connected to DB");

await initializeLists();

const client = new Client({
	intents: GatewayIntentBits.Guilds | GatewayIntentBits.GuildVoiceStates | GatewayIntentBits.GuildMembers,
});

const abortController = new AbortController();

const elevatorHandlerFuture = elevatorHandler(client, dbclient, abortController.signal);
// const settingsChangeHandler = setupSettingsChangeHandler({ client, mongodb: dbclient });

let renameallRestartedFutures: Promise<void>[] | null = null;

let exitCalled = false;
const exitListener = (signal: string) => {
	if (exitCalled) {
		return;
	}
	exitCalled = true;
	logger.debug(`Called exitListener (${signal})`);

	const destroyRestartedRenamealls = async () => {
		if (renameallRestartedFutures === null) {
			return null;
		}

		return Promise.all(renameallRestartedFutures);
	};

	const destroy = async () => {
		await client.destroy();
		await dbclient.close();
	};
	
	abortController.abort("The process is exiting");
	elevatorHandlerFuture.catch(e => {
		if (e instanceof Error && e.name === "AbortError") {
			return;
		}
		logger.error("Error occurred in elevator handler", { error: e as unknown });
	})
		.then(destroyRestartedRenamealls, destroyRestartedRenamealls)
		.then(destroy, destroy) // Apparently finally doesn't take promises, or the types are wrong
		.then(
			() => {
				logger.debug("Exiting gracefully");
			},
			(e) => {
				logger.error("Got an error while exiting", { error: e as unknown });

				// We have to forcefully exit, since who knows what went wrong
				process.exit(1);
			}
		);
};

process.on("SIGINT", exitListener)
process.on("SIGTERM", exitListener)

client.once('ready', async client => {
	await registerGlobalCommands(dbclient, client.application.id);

	renameallRestartedFutures = await setupRestartedRenameall({
		client,
		mongodb: dbclient,
		abortSignal: abortController.signal,
	});

	logger.info(`Ready and serving ${client.guilds.cache.size} guild(s)`, {
		username: client.user.tag,
		applicationId: client.application.id,
	});
});

client.on('interactionCreate', async interaction => {
	if (interaction.isChatInputCommand()) {
		const handler = slashCommandsHandlerMap.get(interaction.commandName);
		try {
			await handler?.({
				interaction,
				mongodb: dbclient,
				abortSignal: abortController.signal,
			});
		} catch (e) {
			logger.error("Uncaught exception in slash command handler, continuing regardless", { exception: e });
		}
	}

	if (interaction.isMessageComponent()) {
		await messageComponentHandler({ interaction, mongodb: dbclient });
	}
});

client.on('warn', (message) => {
	logger.warn(message, { from: "discord.js" });
});

client.on('debug', (message) => {
	logger.debug(message, { from: "discord.js" });
});

await client.login(discordToken);
