import { SlashCommandBuilder } from "discord.js";
import { logger } from "../logger";
import type { SlashCommand, SlashCommandContext } from "../types";
import { startElevatorTrial, makeSubcommand as makeStartSubcommand } from "./elevator_trial_start";
import { registerContestants, makeSubcommand as makeRegisterSubcommand } from "./elevator_trial_register";

export async function handler(ctx: SlashCommandContext) {
	const { interaction } = ctx;
	const subcommand = interaction.options.getSubcommand(true);

	if (subcommand === "start") {
		await startElevatorTrial(ctx);
		return;
	}

	if (subcommand === "register") {
		await registerContestants(ctx);
		return;
	}

	logger.error("Invalid subcommand", { interaction });
	await interaction.reply({
		content: "Invalid subcommand",
		ephemeral: true,
	});
}

export const name = "elevator-trial";

export function makeBuilder() {
	const builder = new SlashCommandBuilder();
	builder
		.setName(name)
		.setDescription("Starts an Elevator Trial in a specific channel")
		.setDMPermission(false)
		.addSubcommand(makeStartSubcommand)
		.addSubcommand(makeRegisterSubcommand)
	return builder;
}

const command: SlashCommand = {
	handler,
	name,
	makeBuilder,
};
export default command;
