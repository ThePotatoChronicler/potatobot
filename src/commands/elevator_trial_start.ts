import { ChannelType, InteractionReplyOptions, SlashCommandSubcommandBuilder } from "discord.js";
import { logger } from "../logger";
import type { SlashCommandContext, ElevatorTrial } from "../types";
import { DateTime } from "luxon";
import { oneLine } from "common-tags";

export async function startElevatorTrial({ interaction, mongodb: dbc }: SlashCommandContext) {
	if (!interaction.inCachedGuild()) {
		// I have forgotten why I wrote this
		// TODO: If you're bored, replace this with a fetch
		logger.error("Somehow, received an uncached guild, check your intents!", {interaction}); 
		await interaction.reply({
			content: "An internal error has occurred and will be inspected soon",
			ephemeral: true,
		});
		return;
	}

	// FIXME: This doesn't check for the permissions of the member

	const col = dbc.db("global").collection<ElevatorTrial>("elevator_trials");

	const trialChannel = interaction.options.getChannel("channel", true);
	const statusChannel = interaction.options.getChannel("status_channel", false);
	const contestantRole = interaction.options.getRole("contestant_role", false);
	const competitorTimeout = interaction.options.getInteger("timeout", false) ?? 20;

	if (trialChannel.type !== ChannelType.GuildVoice && trialChannel.type !== ChannelType.GuildStageVoice) {
		await interaction.reply({
			content: "`channel` should be a voice channel",
			ephemeral: true,
		});
		return;
	}

	const guildMe = await trialChannel.guild.members.fetchMe();
	if (contestantRole !== null) {
		const roleComparison = contestantRole.comparePositionTo(guildMe.roles.highest);
		if (roleComparison >= 0 || !guildMe.permissions.has("ManageRoles")) {
			await interaction.reply({
				content: "I don't have high enough permissions to remove that role from contestants",
				ephemeral: true,
			})
			return;
		}
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
				statistics: [],
			};
			await col.insertOne(newTrial, { session });
		})
	})

	if (interactionReply !== null) {
		await interaction.reply(interactionReply);
		return;
	}

	const plural = participants.size === 1 ? "" : "s";
	logger.info("Started new elevator trial", { participants });
	await interaction.reply({
		content: `Created a new elevator trial with ${participants.size} participant${plural}`,
		ephemeral: true,
	})
}

export function makeSubcommand(command: SlashCommandSubcommandBuilder): SlashCommandSubcommandBuilder {
	command
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
		);

	return command;
}
