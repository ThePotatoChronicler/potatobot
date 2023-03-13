import { Setting, SettingValueType } from "../types";

const setting: Setting = {
	name: "enable_push_emoji",
	description: "Enables the push_emoji command",
	frontendName: "Enable Push Emoji",
	color: "DarkGold",

	valueType: SettingValueType.boolean,
	defaultValue: false,
};
export default setting;
