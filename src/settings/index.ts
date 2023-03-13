import { ActionRowBuilder, ButtonBuilder, ButtonStyle, EmbedBuilder, StringSelectMenuBuilder } from "discord.js";
import type { ClientSession, FindOptions, MongoClient } from "mongodb";
import { logger } from "../logger";
import type { InteractionHandlerContext } from "../message_component_handler";
import { Setting, FetchedSetting, DBGuildSettingsData, SettingValueType, SettingsUI } from "../types";
import enable_push_emoji from "./enable_push_emoji";

const settings = [
	enable_push_emoji,
];

export const settingsMap = new Map(settings.map(s => {
	return [s.name, s];
}));

async function fetchCurrentSettings({ mongodb, session }: InteractionHandlerContext, guild: string): Promise<DBGuildSettingsData> {
	const col = mongodb.db("global").collection<DBGuildSettingsData>("guild_settings");
	const currentSettings: DBGuildSettingsData = (await col.findOne({ guild }, { session })) ?? { guild, settings: {} };
	return currentSettings;
}

async function updateSettings<T extends DBGuildSettingsData>(
	{ mongodb, session }: InteractionHandlerContext,
	guild: string,
	settings: T,
): Promise<void> {
	const col = mongodb.db("global").collection<DBGuildSettingsData>("guild_settings");
	await col.replaceOne({ guild }, settings, { session, upsert: true });
}

export async function settingsInteractionHandler(ctx: InteractionHandlerContext) {
	const { interaction, interactionData } = ctx;
	if (!interaction.inGuild()) {
		await interaction.editReply({
			content: "Settings are only supported for guilds right now",
			embeds: [],
			components: [],
		});
		return;
	}

	if (!interaction.inCachedGuild()) {
		logger.error({ interaction }, "Uncached guild");
		await interaction.editReply({
			content: "An error occurred, notify the bot developer, or don't, your choice",
			embeds: [],
			components: [],
		});
		return;
	}

	if (!interaction.member.permissions.has("ManageGuild")) {
		await interaction.reply({
			content: "You need the 'Manage Guild' permission",
			ephemeral: true,
		})
		return;
	}

	const data = interactionData as SettingsUI;
	const setting = settingsMap.get(data.selectedSetting);
	if (setting === undefined) {
		await interaction.editReply({
			content: "This setting never existed, or doesn't exist anymore",
			embeds: [],
			components: [],
		});
		return;
	}

	const guild = interaction.guildId;
	const currentSettings: DBGuildSettingsData = await fetchCurrentSettings(ctx, guild);

	const updated: boolean = (() => {
		const cs = currentSettings.settings;

		const match = interaction.customId.match(/^commands\/settings_ui:boolean_(off|on)$/);
		if (match !== null) {
			const toggle = match[1] as "on" | "off";
			cs[setting.name] = toggle === "on";
			return true;
		}

		// We didn't update anything
		return false;
	})();

	if (updated) {
		await updateSettings(ctx, guild, currentSettings);
		return;
	}

	await interaction.editReply({
		content: "Don't know how to handle this, try again",
		embeds: [],
		components: [],
	});
}

function makeDefaultFetchedSetting(setting: Setting, guild: string): FetchedSetting {
	return {
		...setting,
		currentValue: setting.defaultValue,
		guild,
	} as FetchedSetting;
}

export interface FetchSettingValueContext {
	mongodb: MongoClient,
	session?: ClientSession,

	setting: Setting,
	guild: string,
}

export async function fetchSettingValue({ mongodb, setting, guild, session }: FetchSettingValueContext): Promise<FetchedSetting> {
	const col = mongodb.db("global").collection<DBGuildSettingsData>("guild_settings");

	const findOptions: FindOptions<DBGuildSettingsData> = {};
	if (session) {
		findOptions.session = session;
	}
	const guildSettings = (await col.findOne({ guild }, findOptions))?.settings;

	let value: FetchedSetting;
	if (guildSettings === undefined) {
		value = makeDefaultFetchedSetting(setting, guild);
	} else {
		const receivedSetting = guildSettings[setting.name];
		if (receivedSetting === undefined) {
			value = makeDefaultFetchedSetting(setting, guild);
		} else {
			// Typescript is going crazy here
			value = {
				...setting,
				currentValue: receivedSetting,
				guild,
			} as FetchedSetting;
		}
	}

	return value;
}

export function createEmbedForFetchedSetting(setting: FetchedSetting): EmbedBuilder {
	const embed = new EmbedBuilder()
		.setTitle(setting.frontendName)
		.setColor(setting.color ?? null)
		.setDescription(setting.description)
		.addFields([
			{ name: "Current Value", value: formatFetchedSetting(setting) },
		])
		.setFooter({ text: `Real-Time Options - Setting #1/${settings.length}` });

	return embed;
}

export function formatFetchedSetting(setting: FetchedSetting): string {
	if (setting.valueType === SettingValueType.boolean) {
		return setting.currentValue ? "True" : "False";
	}

	if (setting.valueType === SettingValueType.number) {
		return String(setting.currentValue);
	}

	logger.error({ setting }, "Cannot format");
	return "Unknown";
}

export function createComponentsFromSetting(setting: FetchedSetting): ActionRowBuilder<ButtonBuilder | StringSelectMenuBuilder>[] {
	const index = Array.from(settingsMap.keys()).indexOf(setting.name);

	let settingRow = null;

	if (setting.valueType === SettingValueType.boolean) {
		settingRow = new ActionRowBuilder<ButtonBuilder>();
		const setButton = new ButtonBuilder()
			.setCustomId(`commands/settings_ui:boolean_${setting.currentValue ? "off" : "on"}`)
			.setLabel(setting.currentValue ? "Disable" : "Enable")
			.setStyle(setting.currentValue ? ButtonStyle.Danger : ButtonStyle.Success);
		settingRow.addComponents(setButton);
	}

	const pageCycleRow = new ActionRowBuilder<ButtonBuilder>();

	const pageBackButton = new ButtonBuilder()
		.setCustomId("commands/settings_ui:page_prev")
		.setEmoji("⬅️")
		.setLabel("Previous")
		.setStyle(ButtonStyle.Secondary)
		.setDisabled(index <= 0);

	const pageNextButton = new ButtonBuilder()
		.setCustomId("commands/settings_ui:page_next")
		.setEmoji("➡️")
		.setLabel("Next")
		.setStyle(ButtonStyle.Secondary)
		.setDisabled(index >= (settings.length - 1));

	pageCycleRow.setComponents(pageBackButton, pageNextButton);

	const result = [];

	if (settingRow !== null) {
		result.push(settingRow);
	}

	result.push(pageCycleRow);

	return result;
}
