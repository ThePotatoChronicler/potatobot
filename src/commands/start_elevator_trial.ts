import { ChannelType, InteractionReplyOptions, SlashCommandBuilder } from "discord.js";
import { logger } from "../logger";
import type { SlashCommand, SlashCommandContext, ElevatorTrial } from "../types";
import { DateTime } from "luxon";
import { oneLine } from "common-tags";

export async function handler({ interaction, mongodb: dbc }: SlashCommandContext) {
	if (!interaction.inCachedGuild()) {
		// TODO: If you're bored, replace this with a fetch
		logger.error({interaction}, "Somehow, received an uncached guild, check your intents!")
		await interaction.reply({
			content: "An internal error has occurred and will be inspected soon",
			ephemeral: true,
		})
		return;
	}

	const col = dbc.db("global").collection<ElevatorTrial>("elevator_trials");

	const trialChannel = interaction.options.getChannel("channel", true);
	const statusChannel = interaction.options.getChannel("status_channel", false);
	const contestantRole = interaction.options.getRole("contestant_role", false);
	const competitorTimeout = interaction.options.getInteger("timeout", false) ?? 20;

	if (trialChannel.type !== ChannelType.GuildVoice && trialChannel.type !== ChannelType.GuildStageVoice) {
		await interaction.reply({
			content: "`channel` should be a voice channel",
			ephemeral: true,
		})
		return;
	}

	if (contestantRole !== null) {
		const me = await interaction.guild.members.fetchMe();
		const roleComparison = contestantRole.comparePositionTo(me.roles.highest);
		if (roleComparison >= 0 || !me.permissions.has("ManageRoles")) {
			await interaction.reply({
				content: "I don't have high enough permissions to remove that role from contestants",
				ephemeral: true,
			})
			return;
		}
	}

	const guildMe = trialChannel.guild.members.me;
	if (guildMe === null) {
		logger.error({interaction}, "Can't find myself, possibly wrong intents")
		await interaction.reply({
			content: "An internal error has occurred and will be inspected soon",
			ephemeral: true,
		})
		return;
	}

	if (!trialChannel.permissionsFor(guildMe).has("MoveMembers")) {
		await interaction.reply({
			content: "I lack the permissions to do the event in this channel",
			ephemeral: true,
		})
		return;
	}


	let participants = trialChannel.members;
	if (contestantRole !== null) {
		participants = participants.filter(p => p.roles.cache.has(contestantRole.id))
	}

	if (participants.size === 0) {
		let content = "The target channel is empty";
		if (participants.size < trialChannel.members.size) {
			content = "The target channel doesn't have any contestants (or they're missing the contestant role)"
		}
		await interaction.reply({
			content,
			ephemeral: true,
		})
		return;
	}

	const statusChannelID: string | null = (() => {
		if (statusChannel !== null) {
			return statusChannel.id;
		}

		if (interaction.channel !== null) {
			return interaction.channel.id;
		}

		return null;
	})();

	let interactionReply: InteractionReplyOptions | null = null;

	await dbc.withSession(async session => {
		await session.withTransaction(async () => {
			const possiblyOngoingEvent = await col.findOne({ trialChannel: trialChannel.id }, { session });
			if (possiblyOngoingEvent !== null) {
				interactionReply = {
					content: "There is already an event going on in that channel",
					ephemeral: true,
				}
				return;
			}

			const timeNow = DateTime.now();
			const kickAt = timeNow.plus({ seconds: competitorTimeout }).toJSDate();
			const newTrial: ElevatorTrial = {
				timeout: competitorTimeout,
				trialChannel: trialChannel.id,
				statusChannel: statusChannelID,
				contestantRole: contestantRole === null ? null : contestantRole.id,
				startTime: timeNow.toJSDate(),
				participants: participants.map(p => {
					return {
						id: p.id,
						kickAt,
					}
				}),
			};
			await col.insertOne(newTrial, { session })
		})
	})

	if (interactionReply !== null) {
		await interaction.reply(interactionReply);
		return;
	}

	const plural = participants.size === 1 ? "" : "s";
	logger.info({ participants }, "Started new elevator trial");
	await interaction.reply({
		content: `Created a new elevator trial with ${participants.size} participant${plural}`,
		ephemeral: true,
	})
}

export const name = "elevator-trial";

export function makeBuilder() {
	const builder = new SlashCommandBuilder();
	builder
		.setName(name)
		.setDescription("Starts an Elevator Trial in a specific channel")
		.setDMPermission(false)
		.addSubcommand(
			cmd => cmd
				.setName("start")
				.setDescription("Starts a new elevator trial")
				.addChannelOption(
					o => o
						.setName("channel")
						.setDescription("The channel where the trial should be held")
						.setRequired(true)
						.addChannelTypes(ChannelType.GuildStageVoice, ChannelType.GuildVoice)
				)
				.addRoleOption(
					o => o
						.setName("contestant_role")
						.setDescription("The role of contestants, will be removed when contestants loose")
						.setRequired(false)
				)
				.addIntegerOption(
					o => o
						.setName("timeout")
						.setDescription("How many seconds before competitors are kicked out, defaults to 20")
						.setRequired(false)
						.setMinValue(1)
						.setMaxValue(3600)
				)
				.addChannelOption(
					o => o
						.setName("status_channel")
						.setDescription(
							oneLine`
								Channel to report
								statistics about the trial (including the winner),
								defaults to the current channel
								`
						)
						.setRequired(false)
						.addChannelTypes(ChannelType.GuildText)
				)
		)
	return builder;
}

const obj: SlashCommand = {
	handler,
	name,
	makeBuilder,
};
export default obj;
