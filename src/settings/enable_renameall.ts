import { oneLine } from "common-tags";
import { Setting, SettingValueType } from "../types";

const setting: Setting = {
	name: "enable_renameall",
	description: oneLine`
		Enables the renameall command for the common folk (everyone),
		which is normally only usable by users with 'Manage Nicknames' permission.
		`,
	frontendName: "Enable Renameall",
	color: "Blue",

	valueType: SettingValueType.boolean,
	defaultValue: false,
};
export default setting;
