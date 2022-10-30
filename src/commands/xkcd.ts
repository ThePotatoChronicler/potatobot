import { randomInt } from "crypto";
import type { ChatInputCommandInteraction } from "discord.js";

const MAX = 2690;

export default async function handler(interaction: ChatInputCommandInteraction) {
	const xkcd = interaction.options.getInteger("id", false) ?? randomInt(1, MAX + 1);
	let content = `https://xkcd.com/${xkcd}/`;
	if (xkcd > MAX) {
		content = "Possibly nonexistent yet: " + content;
	}
	await interaction.reply({
		content,
	})
}
