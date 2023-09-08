import { SlashCommandBuilder } from "discord.js";
import package_json from "../../package.json";
import type { SlashCommand, SlashCommandContext } from "../types";

export async function handler({ interaction }: SlashCommandContext) {
	await interaction.reply({
		content: package_json.version
	});
}

export const name = "version";

export function makeBuilder() {
	return new SlashCommandBuilder()
		.setName(name)
		.setDescription("Sends the version of the bot");
}

const command: SlashCommand = {
	handler,
	name,
	makeBuilder,
};
export default command;
