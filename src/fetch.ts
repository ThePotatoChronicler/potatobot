import { default as cachedFetch } from "make-fetch-happen";
import { tmpdir } from "os";

export const fetch = cachedFetch.defaults({
	cachePath: `${tmpdir()}/potatobot-fetch-cache`
});
