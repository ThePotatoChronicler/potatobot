import { randomInt } from "crypto";
import type { ChatInputCommandInteraction } from "discord.js";
import { fetch } from "../fetch";
import type { XKCDResponse } from "../types";

const headers = {
	"accept": "application/json",
}

const latest_url = "https://xkcd.com/info.0.json";

export default async function handler(interaction: ChatInputCommandInteraction) {
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
