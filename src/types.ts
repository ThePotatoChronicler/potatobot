import type { ChatInputCommandInteraction, SlashCommandBuilder } from "discord.js";
import type { MongoClient } from "mongodb";

export type StringNum = `${number}`;

export interface XKCDResponse {
	year: StringNum,
	month: StringNum,
	day: StringNum,
	num: number,
	link: string,
	news: string,
	title: string,
	safe_title: string,
	transcript: string,
	alt: string,
	img: string,
}

export interface SlashCommandContext {
	interaction: ChatInputCommandInteraction,
	mongodb: MongoClient,
}

export interface SlashCommand {
	name: string,
	handler: (ctx: SlashCommandContext) => Promise<void>,
	makeBuilder: () => SlashCommandBuilder,
}

export interface Participant {
	id: string,
	kickAt: Date,
}

export interface ElevatorTrial {
	timeout: number,
	contestantRole: string | null,
	trialChannel: string,
	statusChannel: string | null,
	startTime: Date,
	participants: Participant[],
}
