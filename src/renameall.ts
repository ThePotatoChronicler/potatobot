import { MongoClient } from "mongodb";
import { fetch } from "./fetch";
import _ from "lodash-es";
import { RenameallData, RenameallType } from "./types";
import { DiscordAPIError, Client as DiscordClient, InteractionWebhook, RESTJSONErrorCodes } from "discord.js";
import { logger } from "./logger";

const nounsURL = "https://gist.githubusercontent.com/IsuruMahakumara/f390f2efb9cc93c3df874e2ba690ec70/raw/eec99c5597a73f6a9240cab26965a8609fa0f6ea/english-nouns.txt";
const adjectivesURL = "https://gist.githubusercontent.com/IsuruMahakumara/f390f2efb9cc93c3df874e2ba690ec70/raw/eec99c5597a73f6a9240cab26965a8609fa0f6ea/english-adjectives.txt"

let nounsList: string[] | null = null;
let adjectivesList: string[] | null = null;

async function fetchList(URL: string): Promise<string[]> {
  const response = await fetch(URL);
  return (await response.text()).split('\n');
}

export async function initializeLists() {
  nounsList = await fetchList(nounsURL);
  adjectivesList = await fetchList(adjectivesURL);
}

function replacer(sub: string): string {
    if (sub === "%") {
      return "%";
    }

    if (sub === "%%") {
      return "%";
    }

    if (sub === "%n" || sub === "%N") {
      const s = _.sample(nounsList) as string;
      if (sub === "%N") {
        return _.capitalize(s);
      }
      return s;
    }

    if (sub === "%a" || sub === "%A") {
      const s = _.sample(adjectivesList) as string;
      if (sub === "%A") {
        return _.capitalize(s);
      }
      return s;
    }

    if (sub === "%e" || sub === "%E") {
      const s = _.sample(_.sample([nounsList, adjectivesList])) as string;
      if (sub === "%E") {
        return _.capitalize(s);
      }
      return s;
    }

    return sub;
}

export function makeName(nickFormat: string): string {
  return nickFormat.replaceAll(/%.?/g, replacer);
}

type setupArgs = {
  client: DiscordClient<true>,
	mongodb: MongoClient,
	abortSignal: AbortSignal,
}

export async function setupRestartedRenameall(args: setupArgs): Promise<Promise<void>[]> {
  const { mongodb } = args;
  const renameallCol = mongodb.db("global").collection<RenameallData>("renameall");

  const futures = [];
  
  const cursor = renameallCol.find();
  for await (const renameallData of cursor) {
    const future = generalRenameall(args, renameallData).catch((e) => {
      logger.error("Restarted renameall finished with an error", { error: e as unknown });
    });
    futures.push(future);
  }

  return futures;
}

async function generalRenameall({ client, mongodb, abortSignal }: setupArgs, data: RenameallData) {
  const { guild: guildId, type, interactionToken } = data;

  const renameallCol = mongodb.db("global").collection<RenameallData>("renameall");

  const webhook = new InteractionWebhook(client, client.application.id, interactionToken);
  const reply = await webhook.fetchMessage("@original");

  const guild = await client.guilds.fetch(guildId);
  const members = await guild.members.fetch();

  for (const [memberId, member] of members) {
    if (data.renamedMembers.includes(memberId)) {
      continue;
    }

    let nick: string | null;

    if (type === RenameallType.format) {
      let name = null;
      for (let i = 0; i < 10; i++) {
        name = makeName(data.format);
        if (name.length <= 32) {
          break;
        }
      }
      if (name == null) {
        continue;
      }
      nick = name;
    } else if (type === RenameallType.clear) {
      nick = null;
    } else {
      // For cases where an older version is running at the same time as newer version
      continue;
    }

    const who = await (async() => {
      if (reply === null) {
        return null;
      }

      if (reply.reference === null) {
        return null;
      }

      const reference = await reply.fetchReference();

      return reference.author;
    })();

    try {
      await member.setNickname(nick, `renameall ${type} from ${who?.tag ?? "someone /shrug"}`);
    } catch (e) {
      if (e instanceof DiscordAPIError) {
        if (e.code === RESTJSONErrorCodes.MissingPermissions || e.code === RESTJSONErrorCodes.InvalidFormBodyOrContentType) {
          continue;
        }
      }
    }

    await renameallCol.updateOne({
      guild: guildId,
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
    guild: guildId,
  });


  if (reply !== null) {
    await reply.edit({
      content: "Renamed everyone!",
    });
  }
}