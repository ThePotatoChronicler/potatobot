import type { ChatInputCommandInteraction } from "discord.js";
import { version } from "../../package.json";

export default async function handler(interaction: ChatInputCommandInteraction) {
	await interaction.reply({
		content: version
	});
}
