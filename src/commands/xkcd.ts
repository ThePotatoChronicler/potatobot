import { randomInt } from "crypto";
import { SlashCommandBuilder } from "discord.js";
import { fetch } from "../fetch";
import type { SlashCommand, SlashCommandContext, XKCDResponse } from "../types";

const headers = {
	"accept": "application/json",
}

const latest_url = "https://xkcd.com/info.0.json";

export async function handler({ interaction }: SlashCommandContext) {
	const xkcd = interaction.options.getInteger("id", false);
	let content;
	let ephemeral = false;
	if (xkcd === null) {
		const resp = await fetch(latest_url, { method: "GET", headers });
		const body = await resp.json() as XKCDResponse;
		content = `https://xkcd.com/${randomInt(1, body.num + 1)}`;
	} else {
		const url = `https://xkcd.com/${xkcd}/info.0.json`;
		const resp = await fetch(url, { method: "GET", headers });
		// Caches the response
		await resp.buffer();
		if (resp.ok) {
			content = `https://xkcd.com/${xkcd}`;
		} else {
			ephemeral = true;
			content = "That comic doesn't exist!";
		}
	}

	await interaction.reply({
		content,
		ephemeral,
	})
}

export const name = "xkcd";

export function makeBuilder() {
	const builder = new SlashCommandBuilder();
	builder
		.setName(name)
		.setDescription("Sends a random xkcd comic, or a specific one")
		.addIntegerOption(option =>
			option
				.setName("id").setRequired(false)
				.setDescription("Numeric ID of the comic")
				.setMinValue(1)
		);

	return builder;
}

const command: SlashCommand = {
	handler,
	name,
	makeBuilder,
};
export default command;
