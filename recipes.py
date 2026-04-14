from models import ClipRecipe, RecipeWeights


BUILT_IN_RECIPES = [
    ClipRecipe(
        id="hot-take",
        name="Hot Take",
        description="Opinionated, punchy moments with a strong hook.",
        prompt="Find moments where the speaker makes a strong, standalone tech opinion.",
        target_durations=[20, 35, 45],
        cues=["controversial", "hot take", "opinion", "best", "worst"],
        caption_preset="bold_pop",
        weights=RecipeWeights(hook_strength=1.2, novelty=1.1, qa_value=0.5),
    ),
    ClipRecipe(
        id="qa",
        name="Q&A",
        description="Viewer question and answer segments with practical value.",
        prompt="Find audience questions and the clearest answer segments.",
        target_durations=[30, 45, 60],
        cues=["question", "ask", "why", "how", "?"],
        caption_preset="clean_focus",
        weights=RecipeWeights(topic_match=1.0, speaker_turn=0.9, qa_value=1.3),
    ),
    ClipRecipe(
        id="explainer-tip",
        name="Explainer Tip",
        description="Clear, educational tips or breakdowns.",
        prompt="Find concise tips, explainers, or mini tutorials.",
        target_durations=[30, 45, 75],
        cues=["tip", "here's how", "step", "explain", "because"],
        caption_preset="clean_focus",
        weights=RecipeWeights(topic_match=1.2, confidence=1.0, novelty=0.8),
    ),
    ClipRecipe(
        id="product-demo",
        name="Product Demo",
        description="Hands-on product walkthroughs and feature demonstrations.",
        prompt="Find moments where the speaker demonstrates a product or feature.",
        target_durations=[25, 40, 60],
        cues=["demo", "feature", "device", "phone", "laptop", "show"],
        caption_preset="tech_demo",
        weights=RecipeWeights(topic_match=1.3, hook_strength=0.9, confidence=1.0),
    ),
    ClipRecipe(
        id="news-recap",
        name="News Recap",
        description="Short summaries of launches, rumors, or major updates.",
        prompt="Find short recap moments about releases, launches, or industry news.",
        target_durations=[20, 35, 50],
        cues=["launch", "released", "news", "today", "update", "announced"],
        caption_preset="headline",
        weights=RecipeWeights(topic_match=1.2, novelty=1.2, qa_value=0.4),
    ),
    ClipRecipe(
        id="debate-rant",
        name="Debate/Rant",
        description="Higher-energy disagreement, criticism, or debate moments.",
        prompt="Find energized disagreement, criticism, or rant segments.",
        target_durations=[25, 45, 70],
        cues=["wrong", "problem", "disagree", "hate", "issue", "crazy"],
        caption_preset="bold_pop",
        weights=RecipeWeights(hook_strength=1.1, novelty=1.0, speaker_turn=0.8),
    ),
]

BUILT_IN_RECIPES_BY_ID = {recipe.id: recipe for recipe in BUILT_IN_RECIPES}
