import { oneLine } from "common-tags";
import { DiscordAPIError, GuildEmoji, SlashCommandBuilder } from "discord.js";
import { fetchSettingValue } from "../settings";
import type { SlashCommand, SlashCommandContext } from "../types";

export async function handler({ interaction, mongodb }: SlashCommandContext) {
	if (!interaction.inCachedGuild()) {
		await interaction.reply({
			content: "This is a guild-only command",
			ephemeral: true,
		});
		return;
	}

	const me = await interaction.guild.members.fetchMe();
	if (!me.permissions.has("ManageEmojisAndStickers")) {
		await interaction.reply({
			content: "I lack the permissions to execute this command",
			ephemeral: true,
		});
		return;
	}

	await interaction.deferReply();

	const enabled = await fetchSettingValue({ guild: interaction.guildId, mongodb, setting: "enable_push_emoji" });
	if (!interaction.member.permissions.has("ManageEmojisAndStickers") && !enabled) {
		await interaction.followUp({
			content: "You lack the permission to use this command",
			ephemeral: true,
		});
		return;
	}

	const emojiName = interaction.options.getString("emoji_name", true);
	const attachment = interaction.options.getAttachment("picture", true);
	if (attachment.contentType === null) {
		await interaction.followUp({
			content: "Invalid attachment, must be a valid emoji",
			ephemeral: true,
		});
		return;
	}

	if (!(["image/png", "image/jpeg"].includes(attachment.contentType))) {
		await interaction.followUp({
			content: "Invalid attachment, must be a valid emoji",
			ephemeral: true,
		});
		return;
	}

	const memberName = `${interaction.member.user.username}#${interaction.member.user.discriminator}`;
	const reason = `push_emoji command executed by member ${memberName}`;

	let newEmoji = null;
	while (newEmoji === null) {
		try {
			newEmoji = await interaction.guild.emojis.create({
				attachment: attachment.url,
				name: emojiName,
				reason,
			})
		} catch (error) {
			if (error instanceof DiscordAPIError && error.code === 30008) {
				const emojis = await interaction.guild.emojis.fetch();
				const oldest = emojis.reduce((a, v) => {
					if (v.createdTimestamp < a.createdTimestamp) {
						return v;
					} else {
						return a;
					}
				}, emojis.at(0) as GuildEmoji)
				await oldest.delete(reason);
				continue;
			}
			if (error instanceof DiscordAPIError && error.code === 50035) {
				await interaction.followUp({
					content: "Invalid emoji name",
					ephemeral: true,
				});
				return;
			}
			throw error;
		}
	}

	await interaction.followUp({
		content: `Created new emoji: ${newEmoji.toString()}`,
	});
}

export const name = "push_emoji";
export const description = oneLine`
	Adds a new emoji, deleting the oldest one if there are too many
`;

export function makeBuilder() {
	const builder = new SlashCommandBuilder();
	builder
		.setName(name)
		.setDescription(description)
		.setDMPermission(false)
		.addStringOption(option =>
			option
				.setName("emoji_name")
				.setDescription("The name of the emoji to create")
				.setMinLength(2)
				.setMaxLength(32)
				.setRequired(true)
			)
		.addAttachmentOption(option =>
			option
				.setName("picture")
				.setDescription("The picture to use as an emoji")
				.setRequired(true)
			);

	return builder;
}

const command: SlashCommand = {
	handler,
	name,
	makeBuilder,
};
export default command;
