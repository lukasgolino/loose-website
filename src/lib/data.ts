// Site copy and game facts. Facts mirror ../loose/GAME.md and ../loose/data (levels, arrows, phrases.cfg); update
// both together.

export const STEAM_URL = ""; // Steam store page, once it exists ("" = "coming soon")
export const KILN_URL = "https://lukasgolino.com/kiln-website/";
export const SEGAN_URL = "https://segan.top";
export const PAGAN_URL = "https://pagan.top";

export interface Clip {
  /** public/video/<id>.mp4|.webm|.jpg (muted loop). Shown only once its mp4 exists. */
  id: string;
  /** The game's own callout for the moment (data/phrases.cfg). */
  call: string;
  title: string;
  blurb: string;
}

/** The fun moments, in page order. */
export const CLIPS: Clip[] = [
  {
    id: "killcam",
    call: "BULLSEYE!",
    title: "The kill cam",
    blurb: "Lock on and the world drops to a crawl. Watch your arrow find its mark, then watch him find the floor.",
  },
  {
    id: "keg",
    call: "KABOOM!",
    title: "Powder kegs",
    blurb: "Sappers carry kegs to your gate. Put an arrow in the keg first and the crowd round it goes up with it.",
  },
  {
    id: "bowl",
    call: "STRIKE!",
    title: "Human skittles",
    blurb: "Hit a man hard enough and he takes the column behind him down too. Three in one shot is a strike.",
  },
  {
    id: "bridge",
    call: "DRAWBRIDGE!",
    title: "Mind the gap",
    blurb: "Shoot the lever and both leaves snap up, flinging everyone on the bridge into the river.",
  },
  {
    id: "fire",
    call: "ABLAZE!",
    title: "Spreading the cheer",
    blurb: "A burning man is a fire hazard. Fling him into the hay, the kegs or his friends and see what happens.",
  },
  {
    id: "trebuchet",
    call: "AIRMAIL!",
    title: "Own goal",
    blurb: "Cut a trebuchet's trigger rope and it fires early: the stone drops on its own side and the winders go up with the sling.",
  },
];

/** The hero loop: the arrow in flight. */
export const HERO_CLIP = "flight";

export interface Arrow {
  id: string;
  name: string;
  text: string;
}

export const ARROWS: Arrow[] = [
  { id: "standard", name: "Standard", text: "Quick and nimble. Eyes score triple." },
  { id: "fire", name: "Fire", text: "Lights men, hay bales, oil and kegs. Fire spreads." },
  { id: "heavy", name: "Heavy", text: "Slow, but it knocks shields and helmets clean off." },
  { id: "bodkin", name: "Bodkin", text: "A needle point that goes straight through armour." },
  { id: "split", name: "Split", text: "Splits into three in flight. Three arrows, three problems." },
];

export interface Level {
  n: string;
  title: string;
  idea: string;
}

export const LEVELS: Level[] = [
  { n: "I", title: "Field Day", idea: "You are the arrow. Steer it into a soldier." },
  { n: "II", title: "Shields Up", idea: "Shieldbearers block from the front: come from above or the side." },
  { n: "III", title: "Ladders", idea: "Hit one ladder carrier and they all fall over. Tip the oil onto climbers." },
  { n: "IV", title: "The Ram", idea: "A covered ram heads for the gate. Cut the cover rope." },
  { n: "V", title: "Trebuchets", idea: "Hit the trigger rope: it fires short, onto its own side." },
  { n: "VI", title: "The Tower", idea: "A siege tower full of soldiers. Pull the wheel pin." },
  { n: "VII", title: "Night Siege", idea: "Torchlight, snow and fire everywhere. Split arrows." },
  { n: "VIII", title: "The Grand Assault", idea: "Everything they've got, led by the General and his very big helmet." },
];
