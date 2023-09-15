import { ActionRowBuilder, ButtonBuilder, ButtonStyle, EmbedBuilder, StringSelectMenuBuilder } from "discord.js";
import type { ClientSession, FindOptions, MongoClient } from "mongodb";
import { logger } from "../logger";
import type { InteractionHandlerContext } from "../message_component_handler";
import { Setting, FetchedSetting, DBGuildSettingsData, SettingValueType, SettingsUI, InteractionData } from "../types";
import enable_push_emoji from "./enable_push_emoji";
import enable_renameall from "./enable_renameall";

const settings: Setting[] = [
	enable_push_emoji,
	enable_renameall,
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
	const { interaction, interactionData, mongodb, session } = ctx;
	if (!interaction.inGuild()) {
		await interaction.editReply({
			content: "Settings are only supported for guilds right now",
			embeds: [],
			components: [],
		});
		return;
	}

	if (!interaction.inCachedGuild()) {
		logger.error("Uncached guild", { interaction });
		await interaction.editReply({
			content: "An error occurred, notify the bot developer, or don't, your choice",
			embeds: [],
			components: [],
		});
		return;
	}

	if (!interaction.member.permissions.has("ManageGuild")) {
		await interaction.followUp({
			content: "You need the 'Manage Guild' permission",
			ephemeral: true,
		})
		return;
	}

	const settingsData = interactionData as SettingsUI;
	const setting = settingsMap.get(settingsData.selectedSetting);
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

	let shownSetting: Setting = setting;

	const changedSettings = (() => {
		const match = interaction.customId.match(/^commands\/settings_ui:boolean_(off|on)$/);
		if (match === null) {
			return false;
		}
		const toggle = match[1] as "on" | "off";
		currentSettings.settings[setting.name] = toggle === "on";
		return true;
	})();

	const changedPage = (() => {
			const match = interaction.customId.match(/^commands\/settings_ui:page_(prev|next)$/)
			if (match === null) {
				return false;
			}

			const direction = match[1] as "prev" | "next";
			const index = getSettingIndex(setting.name);
			const newIndex = index + (direction === "prev" ? -1 : 1);

			const newSettingName = Array.from(settingsMap.keys())[newIndex];
			if (newSettingName === undefined) {
				// We assume there is atleast one setting
				shownSetting = settings[0] as Setting;
				return true;
			}

			// We assume there is atleast one setting
			shownSetting = settingsMap.get(newSettingName) as Setting;
			return true;
	})();

	const interactionsCol = mongodb.db("global").collection<InteractionData>("interactions");

	const currentValue = currentSettings.settings[shownSetting.name] ?? shownSetting.defaultValue;

	if (changedSettings) {
		await updateSettings(ctx, guild, currentSettings);
	}

	if (changedPage) {
		await interactionsCol.updateOne({
			interactionId: settingsData.interactionId,
		}, {
			$set: {
					selectedSetting: shownSetting.name,
			},
		}, {
			session,
		});
	}

	if (changedPage || changedSettings) {
		const fetchedSetting: FetchedSetting = {
			...shownSetting,
			currentValue,
			guild,
		} as FetchedSetting;

		await interaction.editReply({
			embeds: [createEmbedForFetchedSetting(fetchedSetting)],
			components: createComponentsFromSetting(fetchedSetting),
		});
	}
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

	setting: Setting | string,
	guild: string,
}

export async function fetchSettingValue({ mongodb, setting, guild, session }: FetchSettingValueContext): Promise<FetchedSetting> {
	let realSetting;
	if (typeof setting === "string") {
		const mappedSetting = settingsMap.get(setting);
		if (mappedSetting === undefined) {
			logger.error("Received non-existent setting name", { setting });
			throw Error("Setting doesn't exist");
		}
		realSetting = mappedSetting;
	} else {
		realSetting = setting;
	}

	const guildSettingsCol = mongodb.db("global").collection<DBGuildSettingsData>("guild_settings");

	const findOptions: FindOptions<DBGuildSettingsData> = {};
	if (session) {
		findOptions.session = session;
	}
	const guildSettings = (await guildSettingsCol.findOne({ guild }, findOptions))?.settings;

	let value: FetchedSetting;
	if (guildSettings === undefined) {
		value = makeDefaultFetchedSetting(realSetting, guild);
	} else {
		const receivedSetting = guildSettings[realSetting.name];
		if (receivedSetting === undefined) {
			value = makeDefaultFetchedSetting(realSetting, guild);
		} else {
			// Typescript is going crazy here
			value = {
				...realSetting,
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
		.setFooter({ text: `Real-Time Options - Setting #${getSettingIndex(setting.name) + 1}/${settings.length}` });

	return embed;
}

export function formatFetchedSetting(setting: FetchedSetting): string {
	if (setting.valueType === SettingValueType.boolean) {
		return setting.currentValue ? "True" : "False";
	}

	if (setting.valueType === SettingValueType.number) {
		return String(setting.currentValue);
	}

	logger.error("Cannot format", { setting });
	return "Unknown";
}

function getSettingIndex(setting_name: string): number {
	return Array.from(settingsMap.keys()).indexOf(setting_name);
}

export function createComponentsFromSetting(setting: FetchedSetting): ActionRowBuilder<ButtonBuilder | StringSelectMenuBuilder>[] {
	const index = getSettingIndex(setting.name);

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
