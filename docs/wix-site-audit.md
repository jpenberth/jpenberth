# Wix site audit — jason66348.wixsite.com/mysite-1

Captured 2026-10-03 from the live free Wix site (HTML + assets; no browser render).

## Brand
- Site title: "J. Penberth" / "J. Penberth Rabold". Tagline: `[ DIRECTOR & STORYTELLER ]`
- Logo: black handwritten signature "J. Penberth Rabold / STORYTELLER" on white (needs the original vector/PNG with transparent bg)
- Footer: © 2021 by J. Penberth Rabold; mailing-list signup on every page

## Pages (nav: HOME · FILMOGRAPHY · BIOGRAPHY · CONTACT · More)
| Page | Wix slug | Content |
|---|---|---|
| Home | /home | Full-bleed looping video (1280x720 source, ~15s, letterboxed), tagline, ACCOLADES row (Caketown, Way Too Soon, Ghosts of War laurels), Filmmakers Collaboration Challenge 2019: Runner-Up Jury Prize + Runner-Up Best Visuals (Connected) |
| Filmography | /work | Video gallery: Way Too Soon (Jacob Luttrell, 4:36), Connected (6:19), Familiar Faces (6:11), One Gloved Rider (5:18) |
| Biography | /biography | Bio + filmography list (Connected 2019, Almost Super 2020, One Gloved Rider 2020, Familiar Faces 2020, Toxic City - coming soon, Devilwood - coming soon) |
| Contact | /contact | Bookings / Production company / General inquiries |
| (unused) | /events, /schedule, /event, /fullscreen-page | Wix template leftovers — drop |

## Design
- Fonts: Raleway, Playfair Display (headings/body); Wix-only: DIN Next Light, Brandon Grotesque Light, Helvetica
- Colors: #000000 and #FFFFFF dominant; accent #2b5672 (steel blue); greys #BABABA / #5d5d61
- Look: dark, cinematic; video behind content with ~0.4–0.7 opacity overlays and an `overlay` blend-mode texture layer
- Hero video: video.wixstatic.com/video/b02a05_f6f36104f1754ab083c2e983fcb472b3 (480p/720p/1080p mp4)

## Video embeds on Filmography (hosted externally, not on Wix)
- YouTube: 9kDtB5f8ZFA, H98SCB794-o, T78zgx4-O2k
- Vimeo: 531735478
- Vimeo account referenced: vimeo.com/lydianpictures

## Gaps / fixes for the rebuild
- No per-project pages (bad for SEO) -> one URL per film with VideoObject/Movie schema
- Text is thin; no credits, cast, press, awards detail
- "Challange" typo in accolades
- No photos of Jason; no stills for most projects
