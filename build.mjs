import * as esbuild from "esbuild";
import yargs from "yargs";
import { hideBin } from "yargs/helpers";

const argv = await yargs(hideBin(process.argv))
	.boolean("--watch")
	.boolean("--replit")
	.argv;

const replit = argv["--replit"] === true;
const watch = argv["--watch"] ?? false;

if (watch) {
	console.error("'--watch' temporarily removed because esbuild spontaneously exits when using context")
	process.exit(1);
}

const outfile = (() => {
	if (replit) {
		return "dist/main_replit.mjs"
	}
	return "dist/main.mjs";
})();

const minify = (() => {
	if (replit) {
		return true;
	}
	return false;
})();

await esbuild.build({
	entryPoints: [ "src/main.ts" ],
	outfile,
	format: "esm",
	platform: "node",
	target: [
		"node18"
	],
	sourcemap: "inline",
	bundle: true,
	minify,
	external: [
		'./node_modules/*'
	],
});
