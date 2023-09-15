import { DiscordAPIError, RESTJSONErrorCodes, SlashCommandSubcommandBuilder } from "discord.js";
import { RenameallData, RenameallFormatData, RenameallType, SlashCommandContext } from "../types";
import { stripIndent } from "common-tags";
import { makeName } from "../renameall";

export async function renameallFormat({ interaction, mongodb, abortSignal }: SlashCommandContext<"cached"> ) {  
  const renameallCol = mongodb.db("global").collection<RenameallData>("renameall");

  const maybe_this_guild_renameall = await renameallCol.findOne({
    guild: interaction.guildId,
  });

  if (maybe_this_guild_renameall !== null) {
    await interaction.reply({
      content: "An ongoing renameall is already going on in this guild",
      ephemeral: true,
    });
    return;
  }

  const nickformat = interaction.options.getString("format", true);

  await interaction.reply({
		content: stripIndent`
      Renaming everyone...
      Format: ${nickformat}
    `,
	});


  const data: RenameallFormatData = {
    guild: interaction.guildId,
    renamedMembers: [],
    type: RenameallType.format,
    format: nickformat,
    interactionToken: interaction.token,
  };

  interaction.token

  await renameallCol.insertOne(data);

  const members = await interaction.guild.members.fetch();

	for (const [_, member] of members) {
    try {
      let name = null;
      for (let i = 0; i < 10; i++) {
        name = makeName(nickformat);
        if (name.length <= 32) {
          break;
        }
      }
      await member.setNickname(name, `renameall format command from ${interaction.user.tag}`)
    } catch (e) {
      if (e instanceof DiscordAPIError) {
        if (e.code === RESTJSONErrorCodes.MissingPermissions || e.code === RESTJSONErrorCodes.InvalidFormBodyOrContentType) {
          continue;
        }
      }

      throw e;
    }

    await renameallCol.updateOne({
      guild: interaction.guildId,
    }, {
        $push: {
          "renamedMembers": member.id,
        },
      });

    if (abortSignal.aborted) {
      return;
    }
	}

  await renameallCol.deleteOne({
    guild: interaction.guildId,
  });

	await interaction.editReply({
		content: "Renamed everyone!",
	});
}

export function makeSubcommand(command: SlashCommandSubcommandBuilder): SlashCommandSubcommandBuilder {
  command
    .setName("format")
    .setDescription("Rename everyone using a format string")
    .addStringOption(
      o => o
        .setName("format")
        .setDescription("The format string")
        .setMaxLength(128)
        .setMinLength(1)
        .setRequired(true)
    );
  
  return command;
}
