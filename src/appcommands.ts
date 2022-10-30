import { ContextMenuCommandBuilder, REST, Routes, SlashCommandBuilder } from "discord.js";
import type { MongoClient } from "mongodb";
import { applicationID, discordToken } from "./env";
import { logger } from "./logger";

function getGlobalSlashCommands() {
	return [
		new SlashCommandBuilder()
			.setName("xkcd")
			.setDescription("Sends a random xkcd comic, or a specific one")
			.addIntegerOption(option =>
				option
					.setName("id").setRequired(false)
					.setDescription("Numeric ID of the comic")
					.setMinValue(1)
			),
		new SlashCommandBuilder()
			.setName("version")
			.setDescription("Sends the version of the bot")
	];
}

function getGlobalContextCommands() {
	return [
	];
}

function getGlobalCommands() {
	return [
		...getGlobalSlashCommands(),
		...getGlobalContextCommands(),
	];
}

/*
 * Registers commands if they've changed
 */
async function registerGlobalCommands(db: MongoClient) {
	const rest = new REST().setToken(discordToken);
	const cmds = getGlobalCommands();
	const cmdjson = cmds.map(c => c.toJSON());
	const cmdstring = JSON.stringify(cmdjson);

	let result;
	const colc = db.db("global").collection("metadata");
	await db.withSession(async session => {
		await session.withTransaction(async () => {
			const current = await colc.findOne({ key: "applicationcommands" }, { session });
			if (cmdstring === current?.["value"]) {
				return;
			}

			logger.info("Refreshing appcommands");
			result = await rest.put(Routes.applicationCommands(applicationID), {
				body: cmdjson
			});

			const updateResult = await colc.updateOne(
				{ key: "applicationcommands" },
				{ $set: { value: cmdstring } },
				{ upsert: true, session }
			);

			logger.debug(updateResult, "appcommands.updateResult")
		});
	});
	return result;
}

export {
	registerGlobalCommands,
	getGlobalCommands,
	getGlobalSlashCommands,
	getGlobalContextCommands,
}
