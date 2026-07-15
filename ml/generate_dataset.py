"""
Generates a labeled dataset of short transcript-style text snippets for training
a video category classifier. Categories: tutorial, vlog, interview, review, comedy, educational.

This is original, template-generated text (not scraped from any real video),
built specifically for training purposes.
"""
import csv
import random

random.seed(42)

TEMPLATES = {
    "tutorial": [
        "Today I'm going to show you step by step how to {task}.",
        "In this tutorial we'll walk through {task} from scratch.",
        "Let's open up the {tool} and start by configuring the settings.",
        "First, install the required dependencies before we {task}.",
        "Now click on the button labeled settings and select {option}.",
        "If you run into an error here, double check your {thing}.",
        "This is the most common mistake beginners make when they {task}.",
        "Once you've done that, save the file and run the script again.",
        "Let's break this down into three simple steps you can follow.",
        "By the end of this video you'll be able to {task} on your own.",
        "Make sure you have {tool} installed before continuing.",
        "Here's a quick shortcut that will save you a lot of time.",
    ],
    "vlog": [
        "So today I woke up super early and decided to go grab coffee.",
        "Life has been really hectic lately, but I wanted to share an update.",
        "We ended up driving three hours just to try this new restaurant.",
        "Honestly this week was a rollercoaster, let me tell you what happened.",
        "I've been feeling a bit overwhelmed but things are looking up.",
        "Come with me as I run errands and get ready for the weekend.",
        "My family surprised me with a trip and I still can't believe it.",
        "Just a heads up, this vlog is a bit more personal than usual.",
        "We spent the whole afternoon just walking around the city.",
        "I finally moved into my new apartment and I'm so excited.",
        "Today was one of those slow, cozy days at home with the dog.",
        "Thank you all so much for following along on this journey with me.",
    ],
    "interview": [
        "So tell me, how did you first get started in this industry?",
        "That's such an interesting perspective, can you expand on that?",
        "What advice would you give to someone just starting out?",
        "Looking back, what would you say was the biggest turning point?",
        "Thanks so much for joining me today, I've been looking forward to this.",
        "Let's talk about the challenges you faced early in your career.",
        "How do you balance all these different responsibilities at once?",
        "What's a common misconception people have about your field?",
        "I really appreciate you being so open about that experience.",
        "Before we wrap up, is there anything else you'd like to share?",
        "You mentioned earlier that things didn't go as planned, tell me more.",
        "It's fascinating how your path led you to where you are now.",
    ],
    "review": [
        "Let's talk about the build quality first before we get into performance.",
        "For the price, this product actually punches above its weight.",
        "The battery life lasted about six hours under normal use.",
        "Compared to the previous model, this one feels noticeably faster.",
        "I've been testing this for two weeks and here's what stood out.",
        "The packaging was nice but the setup process was a bit confusing.",
        "On paper the specs look great, but real world performance tells a different story.",
        "Would I recommend this? Let's go over the pros and cons.",
        "The camera quality in low light is where this really shines.",
        "It's a solid option if you're on a budget, but there are trade-offs.",
        "After using it daily, a few issues started to become obvious.",
        "Overall this earns a solid rating, though it's not perfect.",
    ],
    "comedy": [
        "So my roommate thought it would be a great idea to cook without a recipe.",
        "I swear this is the most ridiculous thing that's happened to me all year.",
        "Picture this, I'm standing there and everyone is just staring at me.",
        "You will not believe what my dog did to my favorite shoes.",
        "This skit is entirely based on a true and slightly embarrassing story.",
        "I tried to act natural but honestly I panicked immediately.",
        "The audience lost it the moment I dropped the microphone by accident.",
        "Nobody warned me that this would go so horribly wrong.",
        "At this point I was just laughing at how bad the situation had gotten.",
        "My family still brings this up every single holiday, it's a running joke.",
        "I don't know why I thought that plan would actually work.",
        "This bit gets funnier every time I tell it, I promise.",
    ],
    "educational": [
        "Let's define this concept before we move into the details.",
        "Historically, this event had a major impact on how things developed.",
        "To understand this properly, we need to look at the underlying theory.",
        "This process can be broken down into a few key stages.",
        "Researchers found that this pattern holds true across most cases.",
        "There's an important distinction between these two ideas worth noting.",
        "Let's examine why this happens at a more fundamental level.",
        "This diagram helps illustrate how the different parts interact.",
        "Understanding this principle is essential before moving to the next topic.",
        "Many students find this confusing at first, so let's slow down.",
        "This theory was later challenged by new evidence in the field.",
        "In summary, these three factors explain most of the variation we see.",
    ],
}

FILL_TASK = ["set up a virtual environment", "deploy this app", "connect the database",
             "build a login page", "fix this bug", "optimize this function", "write unit tests"]
FILL_TOOL = ["VS Code", "the terminal", "Docker", "GitHub Desktop", "the command line", "Postman"]
FILL_OPTION = ["dark mode", "auto-save", "the pro plan", "advanced settings"]
FILL_THING = ["API key", "internet connection", "file path", "environment variable"]


def fill(template):
    return (template
            .replace("{task}", random.choice(FILL_TASK))
            .replace("{tool}", random.choice(FILL_TOOL))
            .replace("{option}", random.choice(FILL_OPTION))
            .replace("{thing}", random.choice(FILL_THING)))


def build_transcript(category, num_sentences=8):
    pool = TEMPLATES[category]
    sentences = [fill(random.choice(pool)) for _ in range(num_sentences)]
    return " ".join(sentences)


def main():
    rows = []
    samples_per_category = 40
    for category in TEMPLATES:
        for _ in range(samples_per_category):
            length = random.randint(5, 10)
            text = build_transcript(category, length)
            rows.append((text, category))

    random.shuffle(rows)

    with open("ml/training_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "category"])
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to ml/training_data.csv")


if __name__ == "__main__":
    main()