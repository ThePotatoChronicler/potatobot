import { PermissionFlagsBits, SlashCommandBuilder } from "discord.js";
import type { SlashCommand, SlashCommandContext } from "../types";
import { makeSubcommand as makeFormatSubcommand, renameallFormat } from "./renameall_format";
import { makeSubcommand as makeClearSubcommand, renameallClear } from "./renameall_clear";
import { fetchSettingValue } from "../settings";

export async function handler(ctx: SlashCommandContext) {
	const { interaction, mongodb } = ctx;

	if (!interaction.inCachedGuild()) {
		await interaction.reply({
			content: "This is a guild-only command",
			ephemeral: true,
		});
		return;
	}


	const me = await interaction.guild.members.fetchMe();

	if (!me.permissions.has(PermissionFlagsBits.ManageNicknames)) {
		await interaction.reply({
			content: "I lack the permissions to execute this command (Manage Nicknames)",
			ephemeral: true,
		});
		return;
	}

	const enableRenameall = await fetchSettingValue({ guild: interaction.guildId, setting: "enable_renameall", mongodb });

	if (!enableRenameall) {
		if (!interaction.member.permissions.has(PermissionFlagsBits.ManageNicknames)) {
			await interaction.reply({
				content: "You lack the permissions to run this command (Manage Nicknames)",
				ephemeral: true,
			});
			return;
		}
	}

	const subcommand = interaction.options.getSubcommand(true);

	if (subcommand === "format") {
		// Typescript likes to do stupid shit
		await renameallFormat(ctx as SlashCommandContext<"cached">);
		return;
	}

	if (subcommand === "clear") {
		await renameallClear(ctx as SlashCommandContext<"cached">);
		return;
	}

	await interaction.reply({
		content: "Invalid subcommand",
		ephemeral: true,
	})
}

export const name = "renameall";

export function makeBuilder() {
	const builder = new SlashCommandBuilder();
	builder
		.setName(name)
		.setDescription("Renames everyone")
		.addSubcommand(makeFormatSubcommand)
		.addSubcommand(makeClearSubcommand)
		;

	return builder;
}

const command: SlashCommand = {
	handler,
	name,
	makeBuilder,
};
export default command;
