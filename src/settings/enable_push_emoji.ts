import { oneLine } from "common-tags";
import { Setting, SettingValueType } from "../types";

const setting: Setting = {
	name: "enable_push_emoji",
	description: oneLine`
		Enables the push_emoji command for the common folk (everyone),
		which is normally only usable by users with 'Manage Emoji' permission.
		`,
	frontendName: "Enable Push Emoji",
	color: "DarkGold",

	valueType: SettingValueType.boolean,
	defaultValue: false,
};
export default setting;
