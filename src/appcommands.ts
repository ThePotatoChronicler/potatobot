import { REST, Routes } from "discord.js";
import type { MongoClient } from "mongodb";
import { slashCommands } from "./commands";
import { discordToken } from "./env";
import { logger } from "./logger";

function getGlobalSlashCommands() {
	return slashCommands.map(c => c.makeBuilder());
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
async function registerGlobalCommands(db: MongoClient, applicationID: string) {
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

			logger.debug("appcommands.updateResult", { updateResult });
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
