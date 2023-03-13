import type { MessageComponentInteraction } from "discord.js";
import type { ClientSession, MongoClient } from "mongodb";
import { settingsInteractionHandler } from "./settings";
import type { DBInteractionData } from "./types";

export interface MessageComponentInteractionHandlerContext {
	interaction: MessageComponentInteraction,
	mongodb: MongoClient,
}

export interface InteractionHandlerContext extends MessageComponentInteractionHandlerContext {
	interactionData: DBInteractionData,
	session: ClientSession,
}

export async function handler({ interaction, mongodb }: MessageComponentInteractionHandlerContext) {
	const col = mongodb.db("global").collection<DBInteractionData>("interactions");

	await interaction.deferUpdate();

	await mongodb.withSession(async session => {
		await session.withTransaction(async () => {
			const interactionData = await col.findOne({
				interactionId: interaction.message.id,
			});

			if (interactionData === null) {
				await interaction.update({
					content: "This interaction was not found in our database, can't handle your request"
				})
				return;
			}

			const newCtx: InteractionHandlerContext = {
				interaction,
				interactionData,
				mongodb,
				session,
			};

			if (interactionData.interactionType === "commands/settings_ui") {
				await settingsInteractionHandler(newCtx);
				return;
			}
		});
	});
}
