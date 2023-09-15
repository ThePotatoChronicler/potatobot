import type { CacheType, ChatInputCommandInteraction, ColorResolvable, SlashCommandBuilder } from "discord.js";
import type { ClientSession, MongoClient } from "mongodb";

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

export interface SlashCommandContext<Cached extends CacheType = CacheType> {
	interaction: ChatInputCommandInteraction<Cached>,
	mongodb: MongoClient,
	abortSignal: AbortSignal,
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

export interface ParticipantStatistics {
	userId: string,
	/*
	 * Username when the user left (or won)
	 */
	username: string,
	leftAt: Date,
	duration: number,
	winner: boolean,
}

export interface ElevatorTrial {
	timeout: number,
	contestantRole: string | null,
	trialChannel: string,
	statusChannel: string | null,
	startTime: Date,
	participants: Participant[],
	statistics: ParticipantStatistics[],
}

export enum SettingValueType {
	boolean = "boolean",
	number = "number",
}

export interface SettingMetadata {
	frontendName: string,
	name: string,
	description: string,
	color?: ColorResolvable,
}

export interface FetchedSettingMetadata extends SettingMetadata {
	guild: string,
}

export interface BooleanSetting extends FetchedSettingMetadata {
	valueType: SettingValueType.boolean,
	currentValue: boolean,
	defaultValue: boolean,
}

export interface NumberSetting extends FetchedSettingMetadata {
	valueType: SettingValueType.number,
	currentValue: number,
	defaultValue: number,
}

export type FetchedSetting =
	| BooleanSetting
	| NumberSetting

type NonfetchedSetting<T extends FetchedSetting> = Omit<T, "currentValue" | keyof Omit<FetchedSettingMetadata, keyof SettingMetadata>>

export type Setting = NonfetchedSetting<FetchedSetting>

export function isBooleanSetting(setting: Setting): setting is Omit<BooleanSetting, "currentValue"> {
	return setting.valueType === SettingValueType.boolean;
}
export function isNumberSetting(setting: Setting): setting is Omit<NumberSetting, "currentValue"> {
	return setting.valueType === SettingValueType.number;
}

export interface DBInteractionData {
	/*
	 * The discord Id of the interaction
	 */
	interactionId: string,
	/*
	 * Identifies the handler for this type
	 */
	interactionType: string,
}

export interface SettingsUI extends DBInteractionData {
	interactionType: "commands/settings_ui",
	guild: string,
	channel: string,
	selectedSetting: string,
}

/**
 * Represents all possible interaction data there can be
 */
export type InteractionData =
	| SettingsUI

export interface DBGuildSettingsData {
	guild: string,
	settings: {
		[name: string]: FetchedSetting["currentValue"], // Represents any valid value
	}
}

export type WithMongoSession<T> = T & { session: ClientSession }

export enum RenameallType {
	format = "format",
	clear = "clear",
}

export interface RenameallDataBase {
	guild: string,
	type: string,
	renamedMembers: string[],
	interactionToken: string,
}

export interface RenameallFormatData extends RenameallDataBase {
	type: RenameallType.format,
	format: string,
}

export interface RenameallClearData extends RenameallDataBase {
	type: RenameallType.clear,
}

export type RenameallData =
	| RenameallClearData
	| RenameallFormatData
