# Archipelago Manual for Identity V (Survivors)
An Archipelago Randomizer Manual for Identity V survivors, where you receive characters and their personas (perks) in order to play.

This version only includes survivors, and is inspired by the Dead By Daylight manual, as well as the Identity V implementation for Keymaster's Keep. 

## Important points
- This is a _Mcguffin game_[^1], so you're able to goal once you have enough mcguffins, but you could always create a challenge like "Win one more game after having received enough mcguffins".
- Don't play this on Ranked Matches, since you're potentially weaker than the average player and could ruin the game for your team. There are Unraked/Quick Matches and for-fun gamemodes that would fit better for this.
- Universal Tracker seems to not work with this game sometimes, but it's still playable since the locations are mostly self-explanatory. I'm also working on a Poptracker to help with this.
  - You can look for Character Unlocks items under "!Survivor Unlock" category, then go to that character category to see other items for them.

## Items and locations
You can set a list of which characters to possibly include on the randomization, and a given amount of characters will be selected from this list, and each will have:
### Items
- **Character Unlock -** Allows you to play that character.
- **Class/Unique Challenge Unlock for a Character -** If enabled, items required to complete certain locations with a character.
- **Persona Unlock for a Character -** Allow you to use the corresponding persona with that character.
- **Helper filler items for each character -** Filler items are explained further in this README.

### Locations
Most locations are self-explanatory, but here's their overview.
- **Escape, Draw and Win as a character -** Draw/Win require having 1/2 personas unlocked, respectively.
- **Draw as a character using only a specific persona -** Filler items will help with this.
- **Win as a character using a specific pair of personas.**
- **Unique/Class Challenges for a character -** These locations' requirement changes as specified on the YAML options.

### Filler items
For now, there's only 1 type of filler item that is, for example: "<ins>Acrobat</ins> - HELPER for <ins>Tide Turner</ins>". (Values would change for other character/personas)

This item would allow you to complete the "Draw as <ins>Acrobat</ins> using only <ins>Tide Turner</ins>" location even if you were using another persona together with <ins>Tide Turner</ins>.

[^1]: Archipelago games where you need to receive a certain quantity of a specific item in order to goal.
