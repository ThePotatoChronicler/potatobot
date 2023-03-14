import { oneLine } from "common-tags";
import { ChannelType, SlashCommandSubcommandBuilder } from "discord.js";
import type { SlashCommandContext } from "../types";

export async function registerContestants({ interaction }: SlashCommandContext) {
	if (!interaction.inCachedGuild()) {
		await interaction.reply({
			content: "You can only use this command in a guild",
			ephemeral: true,
		});
		return;
	}

	if (!interaction.member.permissions.has("ManageRoles")) {
		await interaction.reply({
			content: "You lack the permission to use this command, you need the Manage Roles permission",
			ephemeral: true,
		});
		return;
	}

	const contestantRole = interaction.options.getRole("contestant_role", true);

	const me = await interaction.guild.members.fetchMe();
	if (!me.permissions.has("ManageRoles") || (me.roles.highest.position <= contestantRole.position)) {
		await interaction.reply({
			content: oneLine`
				I lack the permission to execute this command, I need Manage Roles
				permission and my highest role needs to be higher than the contestant role
				`,
			ephemeral: true,
		});
		return;
	}

	const trialChannel = interaction.options.getChannel("trial_channel", true);
	if (trialChannel.type !== ChannelType.GuildVoice && trialChannel.type !== ChannelType.GuildStageVoice) {
		await interaction.reply({
			content: "The trial channel must be a Voice Channel or Stage Channel",
			ephemeral: true,
		});
		return;
	}

	for (const member of trialChannel.members.values()) {
		await member.roles.add(contestantRole);
	}

	const members = trialChannel.members.size === 1 ? "member" : "members";
	await interaction.reply({
		content: `Added role ${contestantRole.toString()} to ${trialChannel.members.size} ${members}`,
		allowedMentions: {
			parse: [],
		}
	});
}

export function makeSubcommand(command: SlashCommandSubcommandBuilder): SlashCommandSubcommandBuilder {
	command
		.setName("register")
		.setDescription("Adds contestant role to users in a Voice or Stage channel")
		.addChannelOption(option =>
			option
				.setName("trial_channel")
				.setDescription("The channel with users to add contestant role to")
				.setRequired(true)
				.addChannelTypes(ChannelType.GuildVoice, ChannelType.GuildStageVoice)
			)
		.addRoleOption(option =>
			option
				.setName("contestant_role")
				.setDescription("The role to add to users in selected channel")
				.setRequired(true)
			)
	return command;
}
