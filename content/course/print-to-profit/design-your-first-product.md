::: answer
You don't need to be a designer. Most products that sell are **boxes, holes and text**. In this chapter you'll build your first own design in **Tinkercad** (free, in the browser), test the fit with a tiny print, and learn to add a name in **Bambu Studio** in under a minute. Your own design is what makes your product safe to sell anywhere, including Etsy.
:::

## Why your own design matters

Etsy's rule since 2025: physical items **must be produced from the seller's original design**. A remix of someone else's model, or a printed file you downloaded, isn't enough. Your own design also means:

- Nobody can take down your listing over a license.
- You can change sizes, colors and text whenever buyers ask.
- You can sell the file later on MakerWorld (chapter 10).

::: tip | Start simple
Look at the bestsellers in your niche: many are plain boxes with holes in them. They sell because they fit. Buyers pay for the fit, not for fancy curves.
:::

## The example we'll build

Throughout this guide we follow one product: **a 12-slot holder for Switch game cards.** You'll build it here, step by step. Then build your own product the same way.

::: figure holder | The numbers come from the real card size (31 × 21 × 3 mm) plus a little room.
:::

## Before you open Tinkercad: 3 numbers

::: step ruler | Measure the thing your product holds or fits
Use calipers (about $10 online, the best tool you'll buy) or a ruler. Write down length, width and thickness.

**Example:** a Switch game card is **31 × 21 × 3 mm**.
:::

::: step plus | Add room for the fit
A print is never exactly the size you drew. Add **0.2–0.4 mm on each side** for things that slide in and out.

**Example:** the card is 3 mm thick, so the slot gets **3.8 mm**. It's 21 mm wide, so the slot gets **22 mm**.
:::

::: step box | Decide the outside size
Walls of at least **2 mm** feel solid. Keep the whole product under **25 mm high** if you can: it then often ships as a large letter, which is much cheaper (chapter 8).

**Example:** 12 slots, 8 mm apart, 4 mm floor → **110 × 30 × 18 mm**.
:::

## Build it in Tinkercad, step by step

::: step pointer | Open a new design
Go to **tinkercad.com**, make a free account, click **Create** → **3D Design**. The grid is your build plate. Units are millimetres by default.
:::

::: step box | Make the body
From **Basic Shapes** on the right, drag a **Box** onto the grid. Click it. Click the size numbers that appear next to the handles and type **110** (length), **30** (width) and **18** (height).

In the shape panel, set **Radius** to **2** for soft corners. It instantly looks less "printed".
:::

::: step minus | Make one slot as a hole
Drag a second **Box** onto the grid. In the shape panel, click **Hole**. Set its size to **3.8 × 22 × 14**.

Lift it up so it cuts from the top and leaves a floor: set its height above the grid (the small number above the shape when you drag the black cone on top) to **4**. 4 + 14 = 18, so it ends exactly at the top.
:::

::: step copy | Make 12 slots, exactly 8 mm apart
Set **Snap Grid** (bottom right) to **1 mm**. Select the hole, press **Ctrl+D** (Cmd+D on Mac) to duplicate, then press the right arrow key **8 times**. Now press **Ctrl+D** again **10 times**: Tinkercad repeats the same move every time. You now have 12 holes, 8 mm apart.
:::

::: step align | Center the slots
Select all 12 holes (drag a box around them). Shift-click the body so it's selected too. Click **Align** (top right) and click the middle dots for length and width. Everything is now centered.
:::

::: step layers | Cut the slots
Select everything (**Ctrl+A**) and click **Group**. The holes cut into the body. Done: that's your product.
:::

::: step download | Export the file
Click **Export** → **.STL**. Open the file in Bambu Studio (or your slicer). It should print flat on the bed **without supports**.
:::

::: warn | Before you print the whole thing
Print a **fit test** first. Make a small box (30 × 30 × 18) with 3 slots: **3.6, 3.8 and 4.0 mm** wide. It takes 15 minutes and 5 grams. Pick the slot that fits best and use that size. Every printer and filament is a little different.
:::

## 5 rules for designs that print well

::: yesno | Do | Avoid
+ A flat bottom on the bed: no supports, clean finish
+ Walls of **2 mm** or more: solid in the hand, survives the post
+ Overhangs under **45°**: prints clean without supports
- Thin spikes and tiny text: they break in the post
- Sharp outside corners: use Radius 1–2, it looks better and chips less
:::

## Add a name in Bambu Studio (personalization)

A name can **double** what people will pay, and it takes under a minute per order once you've set it up.

::: step file | Open your model
Open the STL in **Bambu Studio** and place it on the plate as you'll print it.
:::

::: step text | Add the text
Right-click the model → **Add part** → **Text**. Type the name, pick a font and set the size. Use a **bold** font, at least **6 mm** high. Place it on the front or top surface.
:::

::: step layers | Raised or engraved?
- **Raised:** leave it as a part. Set the height to **0.6–1 mm**.
- **Engraved:** right-click the text in the object list → **Change type** → **Negative part**. Use **0.6 mm** or more of depth (at least 3 layers).
:::

::: step palette | Give it a second color (optional)
Right-click the text → **Change filament** → pick a second color. With an AMS it prints in two colors on its own. Without one, add a filament change at the layer where the text starts.
:::

::: step copy | Save it as your template
**File → Save project as** (a .3mf file), for example `card-holder-NAME.3mf`. For each order: open it, double-click the text, change the name, slice, print.
:::

::: tip | Proof before you print
For personalized orders, send the buyer a screenshot of the name in Bambu Studio before you print. One message saves you from reprints over spelling mistakes.
:::

## When you outgrow Tinkercad

Tinkercad is enough for most products that sell. When you want curves, threads or exact edits later, try **Onshape** (free for public projects, in the browser) or **Fusion** (free personal license). Don't switch before your first 10 sales.

::: case Switch game card holder
**Design:** 110 × 30 × 18 mm, 12 slots of 3.8 × 22 mm, 14 mm deep, 8 mm apart, 4 mm floor, Radius 2.

**Fit test:** 3.8 mm held the cards without falling out when turned upside down. 4.0 was too loose.

**Print:** about 45 g of PLA and 2 hours. Flat on the bed, no supports. 4 fit on one plate.

**Personalized version:** a name engraved 0.8 mm into the front, in a second color. Template saved as `card-holder-NAME.3mf`.

*Example numbers for one product. Yours will differ.*
:::

::: do | Your task: design version 1 today
- Measure the thing your product fits, and add your clearance
- Build it in Tinkercad (boxes, holes, Group)
- Print a fit test, then version 1
- Use it for a few days and fix what annoys you
:::

## Next chapter

In **The legal part, done right** you'll check that your product is safe to sell: licenses, Etsy's rules, brand names, product safety and the basics of taxes.
