import { oneLine } from "common-tags";
import { type Client, ChannelType, DiscordAPIError, channelMention, userMention, GuildChannel, TextChannel, StageChannel, VoiceChannel, AttachmentBuilder } from "discord.js";
import { DateTime } from "luxon";
import type { ClientSession, Collection as MongoCollection, MongoClient, WithId } from "mongodb";
import { setInterval } from "timers/promises";
import type { Participant, ElevatorTrial, ParticipantStatistics } from "./types";
import papaparse from "papaparse";
import { logger } from "./logger";

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
	const newStatistics: ParticipantStatistics[] = [...trial.statistics];
	const toRemoveParticipants: string[] = [];
	const trialChannel = await client.channels.fetch(trial.trialChannel);

	if (trialChannel === null) {
		const msg = `Trial ended because channel ${channelMention(trial.trialChannel)} is missing`;
		await reportMessageToStatusChat(client, trial, msg);
		await trials.deleteOne({ _id: trial._id }, { session })
		return;
	}

	if (trialChannel.type !== ChannelType.GuildVoice && trialChannel.type !== ChannelType.GuildStageVoice) {
		const msg = oneLine`
				Trial deleted because channel
				${channelMention(trial.trialChannel)} is of unsupported type
			`;
		await reportMessageToStatusChat(client, trial, msg);
		await trials.deleteOne({ _id: trial._id }, { session })
		return;
	}

	const timeNow = DateTime.now();

	for (const participant of trial.participants) {
		
		if (trialChannel.members.has(participant.id)) {
			newParticipants.push({
				id: participant.id,
				kickAt: timeNow.plus({ seconds: trial.timeout }).toJSDate(),
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
				id: participant.id,
				kickAt: timeNow.plus({ seconds: trial.timeout }).toJSDate(),
			});
			continue;
		}

		const user = await client.users.fetch(participant.id);

		toRemoveParticipants.push(participant.id);
		newStatistics.push({
			leftAt: timeNow.toJSDate(),
			userId: participant.id,
			username: `${user.username}#${user.discriminator}`,
			duration: timeNow.diff(DateTime.fromJSDate(trial.startTime)).toMillis(),
			winner: false,
		});
	}

	await removeContestantsRole(trial, trialChannel, toRemoveParticipants);

	if (newParticipants.length === 0) {
		logger.warn({ trial }, "Couldn't determine winner");
		const msgContent = oneLine`
			Couldn't determine a winner for elevator trial
			in channel ${channelMention(trial.trialChannel)}
		`;
		await reportMessageToStatusChat(client, trial, msgContent);
		await trials.deleteOne({ _id: trial._id }, { session });
		return;
	}

	if (newParticipants.length === 1) {
		const winner = newParticipants.at(0);
		if (winner === undefined) {
			throw Error("Array has length 1 but first index is empty");
		}

		await reportVictory({
			client,
			trial,
			trialChannel,
			trials,
			statistics: newStatistics,
			timeNow,
			winner,
			session,
		});
		return;
	}

	await trials.updateOne({ _id: trial._id }, {
		$set: {
			participants: newParticipants,
			statistics: newStatistics,
		}
	}, { session });
}

interface ReportVictoryContext {
	trials: MongoCollection<ElevatorTrial>,
	trial: WithId<ElevatorTrial>,
	trialChannel: VoiceChannel | StageChannel,
	statistics: ParticipantStatistics[],
	timeNow: DateTime,
	winner: Participant,
	client: Client<true>,
	session: ClientSession,
}

async function reportVictory({trials, trial, trialChannel, statistics, winner, timeNow, client, session}: ReportVictoryContext) {
	logger.debug({ trial, channel: trialChannel, winner }, "Trial victory");
	const msgContent = oneLine`
		The winner for elevator trial
		in channel ${channelMention(trial.trialChannel)}
		is ${userMention(winner.id)}
	`;
	await removeContestantsRole(trial, trialChannel, [ winner.id ]);

	const files = [];


	const winnerUser = await client.users.fetch(winner.id);

	const winnerStatistics: ParticipantStatistics = {
		userId: winner.id,
		duration: timeNow.diff(DateTime.fromJSDate(trial.startTime)).toMillis(),
		leftAt: timeNow.toJSDate(),
		username: `${winnerUser.username}#${winnerUser.discriminator}`,
		winner: true,
	};
	const statisticsWithWinner: ParticipantStatistics[] = [ ...statistics, winnerStatistics ];
	const csvData = statisticsWithWinner.map(s => {
		return {
			...s,
			leftAt: DateTime.fromJSDate(s.leftAt).toFormat("yyyy-MM-dd HH:mm:ss"),
		}
	})


	const csvString = papaparse.unparse(csvData);
	const csvBuffer = Buffer.from(csvString, "utf8");
	const csvAttachment = new AttachmentBuilder(csvBuffer, {
		name: "data.csv",
		description: "Information about the trial",
	});

	files.push(csvAttachment);

	await reportMessageToStatusChat(client, trial, {
		content: msgContent,
		allowedMentions: { parse: [] },
		files,
	});
	await trials.deleteOne({ _id: trial._id }, { session });
}

async function reportMessageToStatusChat(client: Client<true>, trial: ElevatorTrial, options: Parameters<TextChannel["send"]>[0]) {
	if (trial.statusChannel === null) {
		return;
	}

	const statusChannel = await client.channels.fetch(trial.statusChannel);
	if (statusChannel === null || statusChannel.type !== ChannelType.GuildText) {
		return;
	}

	try {
		await statusChannel.send(options)
	} catch (e) {
		if (e instanceof DiscordAPIError) {
			return;
		}
		throw e;
	}
}

async function removeContestantsRole(trial: ElevatorTrial, trialChannel: GuildChannel, contestantList: string[]) {
	if (trial.contestantRole === null) {
		return;
	}

	for (const participant of contestantList) {
		let participantMember;
		try {
			participantMember = await trialChannel.guild.members.fetch(participant);
		} catch (e) {
			if (e instanceof DiscordAPIError) {
				if (e.code === 10007) {
					continue;
				}
			}
			throw e;
		}
		await participantMember.roles.remove(trial.contestantRole);
	}
}
