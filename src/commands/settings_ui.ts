import { SlashCommandBuilder } from "discord.js";
import type { DBInteractionData, SettingsUI, SlashCommand, SlashCommandContext } from "../types";
import { createComponentsFromSetting, createEmbedForFetchedSetting, fetchSettingValue, settingsMap } from "../settings";
import { logger } from "../logger";

export async function handler({ interaction, mongodb }: SlashCommandContext) {
	if (!interaction.inGuild()) {
		await interaction.reply({
			content: "This can only be used in a guild",
			ephemeral: true,
		})
		return;
	}

	if (!interaction.inCachedGuild()) {
		logger.error({ interaction }, "Received uncached guild");
		await interaction.reply({
			content: "If you're seeing this, contact the developer",
			ephemeral: true,
		})
		return;
	}

	const settingVal = settingsMap.values().next();
	if (settingVal.done) {
		await interaction.reply({
			content: "There are no settings",
			ephemeral: true,
		})
		return;
	}

	if (!interaction.member.permissions.has("ManageGuild")) {
		await interaction.reply({
			content: "You need the 'Manage Guild' permission",
			ephemeral: true,
		})
		return;
	}

	const ephemeral = interaction.options.getBoolean("ephemeral", false) ?? true;
	await interaction.deferReply({ ephemeral });

	const setting = settingVal.value;

	const guild = interaction.guildId;

	await mongodb.withSession(async session => {
		await session.withTransaction(async () => {
			const settingFetched = await fetchSettingValue({
				guild,
				mongodb,
				setting,
				session,
			});

			const interactionReply = await interaction.followUp({
				embeds: [createEmbedForFetchedSetting(settingFetched)],
				components: createComponentsFromSetting(settingFetched),
				ephemeral,
			});

			const col = mongodb.db("global").collection<DBInteractionData>("interactions");
			const doc: SettingsUI = {
				guild,
				interactionId: interactionReply.id,
				interactionType: "commands/settings_ui",
				selectedSetting: setting.name,
			};
			await col.insertOne(doc, { session });
		});
	});
}

export const name = "settings_ui";

export function makeBuilder(): SlashCommandBuilder {
	const builder = new SlashCommandBuilder();
	builder
		.setName(name)
		.setDescription("Opens the bot settings UI")
		.setDMPermission(false)
		.addBooleanOption(option =>
			option
				.setName("ephemeral")
				.setDescription("Makes settings visible only to you (defaults to true)")
		);
	return builder;
}

const command: SlashCommand = {
	handler,
	name,
	makeBuilder,
};
export default command;
