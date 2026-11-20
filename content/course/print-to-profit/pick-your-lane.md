Welcome to Print to Profit. This guide has 10 short chapters. Each one ends with a small task. Do the task before you read the next chapter, and in 30 days you'll have a product, a price and real buyers.

::: answer
In this chapter you'll **pick one way to make money** with your printer, set a **realistic first goal**, and block **time in your week** for it. That's it. One decision, made properly.
:::

## Why picking one matters

Most people who try to sell 3D prints do a bit of everything: a keychain here, a Thingiverse model there, a post in a random group. Nothing gets traction, and after a few weeks they quit.

The people who make money pick **one lane** and go deep. They become "the person who makes board game inserts" or "the shop with the great name signs". That focus is what makes buyers remember them.

::: tip | You can change lanes later
Picking one doesn't lock you in forever. It's for the next 30 days. Once you've made your first sales, adding a second lane is easy.
:::

## The 7 lanes

| Lane | First sale | Can grow to | You need |
|---|---|---|---|
| **Print for people nearby** | Days | Low–medium | A printer |
| **Personalized items** | 1–2 weeks | Medium | Basic CAD |
| **Your own designs** | 2–4 weeks | High | Simple CAD |
| **Replacement parts** | 1–2 weeks | Low–medium | Measuring, CAD |
| **Sell the files** | Months | Low–high | Good CAD |
| **Print for businesses** | 2–4 weeks | Medium–high | A reliable printer |
| **Make content** | Months | Low–high | Video, patience |

::: icons
home | Print for people nearby | Friends, neighbours, local groups. Custom bits and fixes. No shop, no shipping.
heart | Personalized items | Names, pets, dates. Buyers pay more for "made for me". Allowed on Etsy.
pencil | Your own designs | Products you design and sell anywhere. Where the real money is.
wrench | Replacement parts | The broken dishwasher wheel. People search for exact parts and pay well.
file | Sell the files | Design once, sell many times. Slow to start, needs a following.
store | Print for businesses | Signs, displays, jigs, prototypes. Bigger orders that repeat.
camera | Make content | Videos of what you make. An audience that later buys from you.
:::

## Quick quiz: which lane fits you?

Answer 4 questions. Pick the answer that's most true for you.

<div class="quiz" id="lane-quiz">
<fieldset><legend>1. How fast do you want your first sale?</legend>
<label><input type="radio" name="q1" value="near,parts"> This week</label>
<label><input type="radio" name="q1" value="pers,biz"> Within a month is fine</label>
<label><input type="radio" name="q1" value="own,files,content"> I'm building something long-term</label>
</fieldset>
<fieldset><legend>2. How do you feel about 3D design (CAD)?</legend>
<label><input type="radio" name="q2" value="near,biz"> Never tried it</label>
<label><input type="radio" name="q2" value="pers,parts"> I can make simple things</label>
<label><input type="radio" name="q2" value="own,files"> I like designing</label>
</fieldset>
<fieldset><legend>3. How many hours a week can you spend?</legend>
<label><input type="radio" name="q3" value="near,pers"> 2–4 hours</label>
<label><input type="radio" name="q3" value="own,parts,biz"> 5–10 hours</label>
<label><input type="radio" name="q3" value="own,content,biz"> More than 10</label>
</fieldset>
<fieldset><legend>4. What sounds most fun?</legend>
<label><input type="radio" name="q4" value="near,parts"> Fixing things and helping people</label>
<label><input type="radio" name="q4" value="pers,own"> Making products people love</label>
<label><input type="radio" name="q4" value="content,files"> Sharing what I make online</label>
<label><input type="radio" name="q4" value="biz"> Dealing with businesses</label>
</fieldset>
<button type="button" class="btn or" id="quizGo">Show my lane</button>
<div class="quizres" id="quizRes" hidden></div>
</div>

<script>
(() => {
  const L = { near: ["Print for people nearby", "Post in a local group this week: \"I have a 3D printer. Need a part, a holder or a gift? Send me a message.\""],
    pers: ["Personalized items", "Pick one item (a name sign or keychain) and make a template where changing the name takes one minute."],
    own: ["Your own designs", "Pick one buyer group and one problem. Chapter 2 shows you how to find a product that sells."],
    parts: ["Replacement parts", "Look around your home for one broken plastic part. Measure it, design it, print it. That's your first listing."],
    files: ["Sell the files", "Start with physical products in parallel. Files sell slowly until you have a following."],
    biz: ["Print for businesses", "List 5 local businesses that could use signs, displays or holders. You'll contact them in chapter 8."],
    content: ["Make content", "Film your next print from start to finish. Post it. Do this every week, and pick a product lane too so you have something to sell."] };
  document.getElementById("quizGo").onclick = () => {
    const score = {}; let n = 0;
    document.querySelectorAll("#lane-quiz input:checked").forEach(i => { n++; i.value.split(",").forEach(k => score[k] = (score[k] || 0) + 1); });
    const box = document.getElementById("quizRes"); box.hidden = false;
    if (n < 4) { box.innerHTML = "<p>Answer all 4 questions first.</p>"; return; }
    const top = Object.entries(score).sort((a, b) => b[1] - a[1])[0][0];
    box.innerHTML = `<p class="qrk">Your lane</p><p class="qrt">${L[top][0]}</p><p><b>Your first move:</b> ${L[top][1]}</p>`;
    try { localStorage.setItem("bp_lane", top); } catch {}
    window.track && track("quiz", top);
    box.scrollIntoView({ behavior: "smooth", block: "center" });
  };
})();
</script>

::: note | Not sure?
If you're torn, pick **Personalized items** or **Your own designs**. They work on every marketplace, including Etsy, and they're where most sellers end up anyway.
:::

## Now make it real

::: step target | Write down your lane
One sentence. Make it specific:

- ❌ "I'll sell 3D prints."
- ✅ "I'll sell **personalized name signs** for **kids' rooms**."
- ✅ "I'll make **organizers** for **board game boxes**."

Notice the pattern: **what** + **for whom**.
:::

::: step chart | Set a realistic first goal
Your first goal is **not** income. It's proof.

| Goal | When |
|---|---|
| First product ready and photographed | Day 10 |
| First sale | Day 20 |
| 10 sales | Day 30–60 |

When you hit 10 sales, you know people want it. Then you grow it.
:::

::: step calendar | Block time in your week
Put it in your calendar like an appointment. For example:

- **Tuesday evening:** design and print (2 hours)
- **Saturday morning:** photos, listing, posts (2 hours)

Four focused hours a week beats a whole weekend once a month.
:::

::: step shield | Know what you won't do
Saying no is part of the plan. For the next 30 days:

- No second lane
- No buying a new printer
- No selling other people's designs
- No pricing by filament cost
:::

::: warn | The trap: endless research
It's tempting to keep reading and planning. Don't. The next chapters each end with a task. Do the task, then move on.
:::

::: do | Your task for this chapter
- Do the quiz above and pick your lane
- Write your lane sentence: **what** + **for whom**
- Put two time blocks in your calendar for this week
- Tell one person what you're doing (it makes you follow through)
:::

## Next chapter

In **Find products that sell** you'll use a simple method to find a product in your lane that people already want, before you print anything.
