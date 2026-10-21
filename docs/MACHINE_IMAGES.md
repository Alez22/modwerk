# Machine images

| Machines | Source | Terms |
| --- | --- | --- |
| Octatrack, Digitakt, Digitone, Digitakt II, Digitone II, Syntakt, Model:Samples, Model:Cycles | [elektronmods.com](https://elektronmods.com) device cut-outs | Used with the site owner's permission, confirmed to the Modwerk owner on 4 October 2026. Credit elektronmods.com with a link wherever the images appear. Remove them if permission is withdrawn. Where the cut-outs originate (for example an Elektron press kit) is not yet recorded. |
| Analog Rytm MKI/MKII, Analog Four MKII, Analog Keys, Analog Heat, Tonverk, Machinedrum, Monomachine | Wikimedia Commons | Each photo's own CC0, CC BY or CC BY-SA licence; author, licence and source are listed in `src/devices/photos.ts`. |

Analog Four MKI has no suitable free photo yet (Commons only has teardown shots), so it shows the line drawing.

The overview shows these images as large tiles, where the elektronmods.com cut-outs (about 240×200 px) look soft on high-density screens. Larger files need the same care: Elektron's press kit is copyrighted and meant for press use, so it needs Elektron's written permission before use here, and elektronmods.com's permission does not extend to images it took from elsewhere.

Files live in `public/machines/`. The app shows a credit line beside each machine's hero image and a full list wherever the machines are shown together: the overview (`#overview`, the landing page) and the forum's front page. Both use `MachinePhotoCredits` in `src/devices/DeviceImage.tsx`. Elektron product names identify the machines only; Modwerk is not affiliated with Elektron.
