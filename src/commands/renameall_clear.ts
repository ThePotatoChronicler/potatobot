import { DiscordAPIError, RESTJSONErrorCodes, SlashCommandSubcommandBuilder } from "discord.js";
import { RenameallClearData, RenameallData, RenameallType, SlashCommandContext } from "../types";
import { stripIndent } from "common-tags";

export async function renameallClear({ interaction, mongodb, abortSignal }: SlashCommandContext<"cached"> ) {  
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

  await interaction.reply({
		content: stripIndent`
      Renaming everyone...
      Clearing names
    `,
	});


  const data: RenameallClearData = {
    guild: interaction.guildId,
    renamedMembers: [],
    type: RenameallType.clear,
    interactionToken: interaction.token,
  };

  await renameallCol.insertOne(data);

  const members = await interaction.guild.members.fetch();

	for (const [_, member] of members) {
    try {
      await member.setNickname(null, `renameall clear command from ${interaction.user.tag}`)
    } catch (e) {
      if (e instanceof DiscordAPIError) {
        if (e.code === RESTJSONErrorCodes.MissingPermissions) {
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
    .setName("clear")
    .setDescription("Clear everyone's nickname");
  
  return command;
}
