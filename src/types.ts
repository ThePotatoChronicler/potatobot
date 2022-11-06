type StringNum = `${number}`;

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
