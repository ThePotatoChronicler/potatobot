import { oneLine } from "common-tags";
import { type Client, ChannelType, DiscordAPIError, channelMention, userMention, GuildChannel, TextChannel } from "discord.js";
import { DateTime } from "luxon";
import type { ClientSession, Collection as MongoCollection, MongoClient, WithId } from "mongodb";
import { setInterval } from "timers/promises";
import { logger } from "./logger";
import type { Participant, ElevatorTrial } from "./types";

export function constructHandler(client: Client<true>, mongodb: MongoClient): [AbortController, Promise<void>] {
	const controller = new AbortController();

	const handlerPromise = handler(client, mongodb, controller.signal);

	return [controller, handlerPromise];
}

export async function handler(client: Client<true>, mongodb: MongoClient, signal: AbortSignal): Promise<void> {
	// TODO: Rewrite so it does nothing while the trial database is empty
	//       using database events, saves connections and reads to the database
	const trials = mongodb.db("global").collection<ElevatorTrial>("elevator_trials");
	for await (const _nothing of setInterval(1000, null, { signal })) {
		await mongodb.withSession(async session => {
			await session.withTransaction(async () => {
				for await (const trial of trials.find({}, { session })) {
					await processTrial(client, trials, session, trial);
				}
			})
		});
	}
}

async function processTrial(
	client: Client<true>,
	trials: MongoCollection<ElevatorTrial>,
	session: ClientSession,
	trial: WithId<ElevatorTrial>
) {
	const newParticipants: Participant[] = [];
	const toRemoveParticipants: string[] = [];
	const timeNow = DateTime.now();
	const trialChannel = await client.channels.fetch(trial["trialChannel"]);

	if (trialChannel === null) {
		logger.info({ trial }, "Trial deleted because channel is missing");
		await trials.deleteOne({ _id: trial._id }, { session })
		return;
	}

	if (trialChannel.type !== ChannelType.GuildVoice && trialChannel.type !== ChannelType.GuildStageVoice) {
		logger.info({ trial }, "Trial deleted because channel is of unsupported type");
		await trials.deleteOne({ _id: trial._id }, { session })
		return;
	}

	for (const participant of trial["participants"]) {

		if (trialChannel.members.has(participant["id"])) {
			newParticipants.push({
				id: participant["id"],
				kickAt: timeNow.plus({ seconds: trial["timeout"] }).toJSDate(),
			});
			continue;
		}

		const kickAt = DateTime.fromJSDate(participant["kickAt"]);
		if (kickAt > timeNow) {
			newParticipants.push(participant);
			continue;
		}

		/* Crash check (aka if we go down and it's been five
		 * seconds after the user should've been kicked, forgive)
		 */
		if (timeNow > kickAt.plus({ seconds: 5 })) {
			newParticipants.push({
				id: participant["id"],
				kickAt: timeNow.plus({ seconds: trial["timeout"] }).toJSDate(),
			});
			continue;
		}

		toRemoveParticipants.push(participant["id"]);
	}

	await removeContestantsRole(trial, trialChannel, toRemoveParticipants);

	if (newParticipants.length === 0) {
		const msgContent = oneLine`
			Couldn't determine a winner for elevator trial
			in channel ${channelMention(trial.trialChannel)}
		`;
		await reportMessageToStatusChat(client, trial, msgContent);
		await trials.deleteOne({ _id: trial._id });
		return;
	}

	if (newParticipants.length === 1) {
		const participant = newParticipants[0];
		if (participant === undefined) {
			throw Error("Array has length 1 but first index is empty");
		}

		const msgContent = oneLine`
			The winner for elevator trial
			in channel ${channelMention(trial.trialChannel)}
			is ${userMention(participant.id)}
		`;
		await removeContestantsRole(trial, trialChannel, [ participant.id ]);
		await reportMessageToStatusChat(client, trial, {
			content: msgContent,
			allowedMentions: { parse: [] }
		});
		await trials.deleteOne({ _id: trial._id });
		return;
	}

	await trials.updateOne({ _id: trial._id }, {
		$set: {
			participants: newParticipants
		}
	})
}

async function reportMessageToStatusChat(client: Client<true>, trial: ElevatorTrial, options: Parameters<TextChannel["send"]>[0]) {
	if (trial.statusChannel !== null) {
		const statusChannel = await client.channels.fetch(trial.statusChannel);
		if (statusChannel !== null && statusChannel.type === ChannelType.GuildText) {
			try {
				await statusChannel.send(options)
			} catch (e) {
				if (e instanceof DiscordAPIError) {
					return;
				}
				throw e;
			}
		}
	}
}

async function removeContestantsRole(trial: ElevatorTrial, trialChannel: GuildChannel, contestantList: string[]) {
	if (trial.contestantRole !== null) {
		for (const participant of contestantList) {
			let pMember;
			try {
				pMember = await trialChannel.guild.members.fetch(participant);
			} catch (e) {
				if (e instanceof DiscordAPIError) {
					if (e.code === 10007) {
						continue;
					}
				}
				throw e;
			}
			await pMember.roles.remove(trial.contestantRole);
		}
	}
}
