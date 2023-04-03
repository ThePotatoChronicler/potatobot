/**
 * This was a prototype for live-editing settings UI with new values,
 * but it can't be done for ephemeral messages.
 *
 * May be used later when this problem is resolved.
 */

import type { Client as DiscordClient } from "discord.js";
import type { ChangeStreamReplaceDocument, MongoClient } from "mongodb";
import type { DBGuildSettingsData, SettingsUI, WithMongoSession } from "./types";

export interface SetupSettingsChangeHandlerContext {
	client: DiscordClient,
	mongodb: MongoClient,
}

export function setupSettingsChangeHandler(ctx: SetupSettingsChangeHandlerContext): [AbortController, Promise<void>] {
	const { mongodb } = ctx;

	const settingsCollection = mongodb.db("global").collection<DBGuildSettingsData>("guild_settings");
	const settingsChangeStream = settingsCollection.watch();

	const controller = new AbortController();
	const cancelSymbol = Symbol();

	const cancelFuture = new Promise<typeof cancelSymbol>((resolve) => {
		controller.signal.addEventListener("abort", () => {
			resolve(cancelSymbol);
		});
	});

	const workerPromise = (async () => {
		while (!controller.signal.aborted) {
			const result = await Promise.any([settingsChangeStream.next(), cancelFuture]);
			if (result === cancelSymbol) {
				break;
			}

			const change = result;

			if (change.operationType !== "replace") {
				continue;
			}

			await updateOldInteractions({ ...ctx, change });
		}

		await settingsChangeStream.close();
	})();

	return [controller, workerPromise];
}

interface UpdateOldInteractionsContext extends SetupSettingsChangeHandlerContext {
	change: ChangeStreamReplaceDocument<DBGuildSettingsData>,
}

async function updateOldInteractions(ctx: UpdateOldInteractionsContext) {
	await ctx.mongodb.withSession(async session => {
		await session.withTransaction(async () => {
			await _updateOldInteractions({ ...ctx, session });
		});
	});
}

async function deleteInteraction({ mongodb, session }: WithMongoSession<UpdateOldInteractionsContext>, interactionId: string) {
	const interactions = mongodb.db("global").collection<SettingsUI>("interactions");
	await interactions.deleteOne({
		interactionId,
	}, { session });

}

async function _updateOldInteractions(ctx: WithMongoSession<UpdateOldInteractionsContext>) {
	const { client, mongodb, session, change } = ctx;

	const interactions = mongodb.db("global").collection<SettingsUI>("interactions");
	const guild = change.fullDocument.guild;
	// TODO: Detect which option changed and fetch only revelant options
	const interactionsToChange = interactions.find({ guild }, { session });

	for await (const interaction of interactionsToChange) {
		const guildFetched = await client.guilds.fetch(guild);
		const channelFetched = await guildFetched.channels.fetch(interaction.channel);
		if (channelFetched === null || !channelFetched.isTextBased()) {
			await deleteInteraction(ctx, interaction.interactionId);
			continue;
		}

		const interactionFetched = await channelFetched.messages.fetch(interaction.interactionId);
		await interactionFetched.edit({
			"content": "Wack",
		})
	}
}
